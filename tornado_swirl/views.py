#!/usr/bin/python
# -*- coding: utf-8 -*-
from urllib.parse import urlparse, urljoin
import inspect
import tornado.web
import tornado.template
from tornado.util import re_unescape
from .settings import SWAGGER_VERSION, URL_SWAGGER_API_LIST, URL_SWAGGER_API_SPEC, api_routes
import json
import re


__author__ = 'serena'


def json_dumps(obj, pretty=False):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')) if pretty else json.dumps(obj)


class SwaggerUIHandler(tornado.web.RequestHandler):
    def initialize(self, static_path, **kwds):
        self.static_path = static_path

    def get_template_path(self):
        return self.static_path

    def get(self):
        discovery_url = urljoin(
            self.request.full_url(), self.reverse_url(URL_SWAGGER_API_LIST))
        self.render('index.html', discovery_url=discovery_url)


class SwaggerResourcesHandler(tornado.web.RequestHandler):
    def initialize(self, api_version, exclude_namespaces, **kwds):
        self.api_version = api_version
        self.exclude_namespaces = exclude_namespaces

    def get(self):
        self.set_header('content-type', 'application/json')
        u = urlparse(self.request.full_url())
        resources = {
            'apiVersion': self.api_version,
            'openapi': SWAGGER_VERSION,
            'basePath': '%s://%s' % (u.scheme, u.netloc),
            'produces': ["application/json"],
            'description': 'Test Api Spec',
            'apis': [{
                'path': self.reverse_url(URL_SWAGGER_API_SPEC),
                'description': 'Test Api Spec'
            }]
        }

        self.finish(json_dumps(resources, self.get_arguments('pretty')))


class SwaggerApiHandler(tornado.web.RequestHandler):
    def initialize(self, api_version, base_url, **kwds):
        self.api_version = api_version
        self.base_url = base_url

    def get(self):
        self.set_header('content-type', 'application/json')
        apis = self.find_api(self.application)  # this is a generator
        specs = {
            'openapi': SWAGGER_VERSION,
            'info': {
                'title': "Sample API",
                'description': "Foo bar",
                'version': self.api_version,
            },
            'servers': [{"url": self.request.protocol + "://" + self.request.host + "/",
                         "description": "This server"
                         }],
            'schemes': ["http", "https"],
            'consumes': ['application/json'],
            'produces': ['application/json'],
            'paths': {path: self.__get_api_spec(path, spec, operations) for path, spec, operations in apis}
        }
        
        self.finish(json_dumps(specs, self.get_arguments('pretty')))

    def __get_models_spec(self, models):
        models_spec = {}
        for model in models:
            models_spec.setdefault(model.id, self.__get_model_spec(model))
        return models_spec

    @staticmethod
    def __get_model_spec(model):
        return {
            'description': model.summary,
            'id': model.id,
            'notes': model.notes,
            'properties': model.properties,
            'required': model.required
        }

    def __get_api_spec(self, path, spec, operations):
        return{
            api[0]: {
                'operationId': str(spec.__name__) + "." + api[0],
                'summary': api[1].summary.strip(),
                'description': api[1].description.strip(),
                'parameters': self.__get_params(api[1]),
                'responses': self.__get_responses(api[1])
                
            } for api in operations
        }

    def __get_params(self, path_spec):
        params = []
        allps = sorted(path_spec.path_params.values(), key=lambda x: x.order) + \
            sorted(path_spec.header_params.values(), key=lambda x: x.order) + \
            sorted(path_spec.query_params.values(), key=lambda x: x.order) + \
            sorted(path_spec.form_params.values(), key=lambda x: x.order) + \
            sorted(path_spec.cookie_params.values(), key=lambda x: x.order) #+ \
            #[path_spec.body_param] body param
        for param in allps:
            if param:
                param_data = {
                    "in": param.ptype,
                    "name": param.name,
                    "required": param.required,
                    "description": str(param.description).strip()
                }
                param_data.update(self.__get_type(param))
                params.append(param_data)

        return params

    def __get_responses(self, path_spec):
        params = {}
        allresps = sorted(path_spec.responses.values(), key=lambda x: x.name)
        for param in allresps:
            if param:
                params[param.name] = {
                    "description": param.description,
                    "content": 
                        self._detect_content(param)  #should return default produces if none, otherwise detect from type
                }

                #TODO: implement examples
        return params

    def _detect_content(self, param):
        
        if param.type not in ('integer','int','string','str','boolean', 'bool', 'number', 'int32', 'int64',
            'float', 'double', "byte", "binary", "date", "date-time", "password" ):
            if param.type == "array":
                return {"application/json": {
                    "schema": {
                        "type": "array",
                        "items": param.itype #TODO: apply refs 
                    }}
                }
            
            return {"application/json": {
                "schema": {
                    "type": param.type #TODO: apply type
                }
            }}
        #TODO: other media types
        return {
            "text/plain": {
                "schema": {
                    "type": param.type
                }
            }
        }
        
        

    def __get_real_type(self, typestr):
        if typestr in ("int", "integer"):
            return {"schema": {
                "type": "integer",
                "format": "int32"
            }}
        
        if typestr == "long":
            return {"schema": {
                "type": "integer",
                "format": "int64"
            }}

        if typestr in ("float", "double"):
            return {"schema": {
                "type": "number",
                "format": typestr
            }}

        if typestr in ("byte", "binary", "date", "password"):
            return {"schema": {
                "type": "string",
                "format": typestr
            }}

        if typestr == "dateTime":
            return {"schema": {
                "type": "string",
                "format": "date-time"
            }}

        if typestr in ("str", "string"):
            return {"schema": {
                "type": "string"
            }}

        if typestr == "bool":
            return {"schema": {
                "type": "boolean"
            }}

        return {"schema": {
            "type": typestr
        }}
        # TODO check if typestr is a reference

    def __get_type(self, param):
        if param.type == "array":
            return {"schema": {
                        "type": "array",
                        "items": {
                            "type": param.itype
                        }
            }
            }
        real_type = self.__get_real_type(param.type)
        return real_type

    @staticmethod
    def find_api(application):
        for route_spec in api_routes():
            # TODO decorate  url
            url, groups = _find_groups(route_spec[0])
            path = url
            h = route_spec[1]
            operations = [(name, member.path_spec) for (
                name, member) in inspect.getmembers(h) if hasattr(member, 'path_spec')]
            # since these ops have the same path, they should have the same path_params in their path_spec, so get the member with
            # the most path_param and set it on all
            if operations:
                path_param_spec = operations[0][1].path_params
                for (_, path_spec) in operations[1:]:
                    if len(path_spec.path_params) > len(path_param_spec):
                        path_param_spec = path_spec.path_params
                for _, ps in operations:
                    ps.path_params = path_param_spec
                vals = path_param_spec.values()
                sorted(vals, key=lambda x: x.order)
                path = url % tuple(
                    ['{%s}' % arg for arg in [param.name for param in vals]]
                )

            else:
                continue

            yield path, h, operations


def _find_groups(url: str):
    """Returns a tuple (reverse string, group count) for a url.

    For example: Given the url pattern /([0-9]{4})/([a-z-]+)/, this method
    would return ('/%s/%s/', 2).
    """
    regex = re.compile(url)
    pattern = url
    if pattern.startswith('^'):
        pattern = pattern[1:]
    if pattern.endswith('$'):
        pattern = pattern[:-1]

    if regex.groups != pattern.count('('):
        # The pattern is too complicated for our simplistic matching,
        # so we can't support reversing it.
        return None, None

    pieces = []
    for fragment in pattern.split('('):
        if ')' in fragment:
            paren_loc = fragment.index(')')
            if paren_loc >= 0:
                pieces.append('%s' + fragment[paren_loc + 1:])
        else:
            try:
                unescaped_fragment = re_unescape(fragment)
            except ValueError:
                # If we can't unescape part of it, we can't
                # reverse this url.
                return (None, None)
            pieces.append(unescaped_fragment)
    return ''.join(pieces), regex.groups

    # @staticmethod
    # def find_api(host_handlers):
    #     for _, handlers in host_handlers:
    #         for spec in handlers:
    #             for (_, member) in inspect.getmembers(spec.handler_class):
    #                 if inspect.ismethod(member) and hasattr(member, 'path_spec'):
    #                     spec_path = spec._path % tuple(
    #                         ['{%s}' % arg for arg in member.func_args])
    #                     operations = [member.path_spec for (name, member) in inspect.getmembers(spec.handler_class)
    #                                   if hasattr(member, 'path_spec')]
    #                     yield spec_path, spec, operations
    #                     break
