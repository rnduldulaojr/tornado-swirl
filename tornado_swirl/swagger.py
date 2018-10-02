"""Swagger decorators"""
import inspect

import tornado.web

from tornado_swirl import docparser
from tornado_swirl.handlers import swagger_handlers
from tornado_swirl.settings import add_api_handler, add_route, add_schema, default_settings


def is_rest_api_method(obj):
    """Determines if function or method object is an HTTP method handler object"""
    return (inspect.isfunction(obj) or inspect.ismethod(obj)) and \
            obj.__name__ in ('get', 'post', 'put', 'delete')


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
        add_api_handler(cls)
        add_route(url, cls, **kwargs)
        return cls
    return _real_decorator


def schema(cls):
    """REST API schema decorator"""
    name = cls.__name__
    doc = inspect.getdoc(cls)
    model_spec = docparser.parse_from_docstring(doc, spec='schema')
    if model_spec:
        cls.schema_spec = model_spec
        add_schema(name, cls)
    return cls

def describe(title='Sample API', description='Sample description', **kwargs):
    default_settings.update({"title": title, "description": description})
    if kwargs:
        default_settings.update(kwargs)

class Application(tornado.web.Application):
    def __init__(self, handlers=None, default_host="", transforms=None, **settings):
        super(Application, self).__init__(
            (swagger_handlers() + handlers) if handlers else swagger_handlers(),
            default_host, transforms, **settings)
