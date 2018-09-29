import re
import inspect
from functools import wraps
from tornado_swirl import docparser
import tornado.web
from tornado_swirl.handlers import swagger_handlers
from tornado_swirl.settings import add_api_handler, add_route

import inspect
from tornado_swirl import docparser


def is_rest_api_method(object):
    return (inspect.isfunction(object) or inspect.ismethod(object)) and object.__name__ in ('get', 'post', 'put', 'delete')


def restapi(url, **kwargs):
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

    name = cls.__name__
    doc = inspect.getdoc(cls)
    model_spec = docparser.parse_from_docstring()
    if model_spec:
        cls.schema_spec = model_spec
        schemas[name] = cls
    return cls
    



class Application(tornado.web.Application):
    def __init__(self, handlers=None, default_host="", transforms=None, **settings):
        super(Application, self).__init__(swagger_handlers() +
                                          handlers, default_host, transforms, **settings)
