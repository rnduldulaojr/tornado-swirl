"""Swagger decorators"""

import inspect
import tornado.web

from tornado_swirl import docparser, settings
from tornado_swirl.handlers import swagger_handlers

class Ref(object):
    def __init__(self, value):
        self.link = value

def is_rest_api_method(obj):
    """Determines if function or method object is an HTTP method handler object"""
    return (inspect.isfunction(obj) or inspect.ismethod(obj)) and \
            obj.__name__ in list(settings.default_settings.get('enabled_methods', []))


def restapi(url, **kwargs):
    """REST API endpoint decorator."""
    def _real_decorator(cls):
        cls.rest_api = True
        cls.tagged_api_comps = []
        members = inspect.getmembers(cls, is_rest_api_method)

        for name, member in members:
            doc = inspect.getdoc(member)
            if not doc:
                continue
            path_spec = docparser.parse_from_docstring(str(doc))
            if path_spec:
                setattr(member, 'path_spec', path_spec) 
                cls.tagged_api_comps.append(name)
        settings.add_api_handler(cls)
        settings.add_route(url, cls, **kwargs)
        return cls
    return _real_decorator


def schema(cls):
    """REST API schema decorator"""
    name = cls.__name__

    #determine super class
    mro = inspect.getmro(cls)
    if not mro:
        mro = (cls,)

    mro = list(mro)
    mro.reverse()
    cls.schema_spec = []
    for item in mro:
        if item.__name__ == 'object':
            continue
        if item.__name__ == name:
            doc = inspect.getdoc(item)
            try:
                model_spec = docparser.parse_from_docstring(doc, spec='schema')
                if model_spec:
                    cls.schema_spec.append(model_spec)
                    settings.add_schema(name, cls)
            except:
                pass
        else: #if class name is a superclass append a ref.
            cls.schema_spec.append(Ref('#/components/schemas/{}'.format(item.__name__)))
    
    return cls

def describe(title='Your API', description='No description', **kwargs):
    """Describe API"""
    settings.default_settings.update({"title": title, "description": description})
    if kwargs:
        settings.default_settings.update(kwargs)

def add_global_tag(name, description=None, url=None):
    settings.add_global_tag(name, description, url)

def add_security_scheme(name, scheme):
    settings.add_security_scheme(name, scheme)

class Application(tornado.web.Application):
    """Swirl Application class"""

    def __init__(self, handlers=None, default_host="", transforms=None, **kwargs):
        super(Application, self).__init__(
            (swagger_handlers() + handlers) if handlers else swagger_handlers(),
            default_host, transforms, **kwargs)
