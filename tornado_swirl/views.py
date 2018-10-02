# -*- coding: utf-8 -*-
from urllib.parse import urlparse, urljoin
import inspect
import tornado.web
import tornado.template
from tornado.util import re_unescape
from .settings import SWAGGER_VERSION, URL_SWAGGER_API_LIST, URL_SWAGGER_API_SPEC, api_routes, get_schemas, is_defined_schema
import json
import re


__author__ = 'rduldulao'


def json_dumps(obj, pretty=False):
    return json.dumps(obj, sort_keys=True, indent=4, separators=(',', ': ')) if pretty else json.dumps(obj)


class SwaggerUIHandler(tornado.web.RequestHandler):
    def initialize(self, static_path, **kwds):
        self.static_path = static_path

    def get_template_path(self):
        return self.static_path

    def get(self):
        discovery_url = urljoin(
            self.request.full_url(), self.reverse_url(URL_SWAGGER_API_SPEC))
        self.render('index.html', discovery_url=discovery_url)

# class SwaggerResourcesHandler(tornado.web.RequestHandler):
#     def initialize(self, api_version, exclude_namespaces, **kwds):
#         self.api_version = api_version
#         self.exclude_namespaces = exclude_namespaces

#     def get(self):
#         self.set_header('content-type', 'application/json')
#         u = urlparse(self.request.full_url())
#         resources = {
#             'apiVersion': self.api_version,
#             'openapi': SWAGGER_VERSION,
#             'basePath': '%s://%s' % (u.scheme, u.netloc),
#             'produces': ["application/json"],
#             'description': 'Test Api Spec',
#             'apis': [{
#                 'path': self.reverse_url(URL_SWAGGER_API_SPEC),
#                 'description': 'Test Api Spec'
#             }]
#         }

#         self.finish(json_dumps(resources, self.get_arguments('pretty')))


class SwaggerApiHandler(tornado.web.RequestHandler):
    def initialize(self, title, description, api_version, base_url, schemes, **kwds):
        self.api_version = api_version
        self.base_url = base_url
        self.title = title
        self.description = description
        self.schemes = schemes

    def get(self):
        self.set_header('content-type', 'application/json')
        apis = self.find_api(self.application)  # this is a generator
        specs = {
            'openapi': SWAGGER_VERSION,
            'info': {
                'title': self.title,
                'description': self.description,
                'version': self.api_version,
            },
            'servers': [{"url": self.request.protocol + "://" + self.request.host + "/",
                         "description": "This server"
                         }],
            'schemes': self.schemes,
            'paths': {path: self.__get_api_spec(path, spec, operations)
                      for path, spec, operations in apis},
        }

        schemas = get_schemas()
        if schemas:
            specs.update(
                {
                    "components": {
                        "schemas": {
                            name: self.__get_schema_spec(schemaCls) for (name, schemaCls) in schemas.items()
                        }
                    }
                }
            )

        self.finish(json_dumps(specs, self.get_arguments('pretty')))

    def __get_schema_spec(self, cls):
        spec = cls.schema_spec
        props = [(prop.name, self._prop_to_dict(prop), prop.required)
                 for (_, prop) in spec.properties.items()]
        required = [name for name, _, req in props if req]

        val = { "type": "object" }
        if required:
            val.update({"required": required})

        val.update({
            "properties": {
                name: d for name, d, r in props
            }
        })

        return val

    def _prop_to_dict(self, prop):
        d = self.__get_type(prop)['schema']
        if d is not None:
            d.update(prop.kwargs)
        return d

    def __get_api_spec(self, path, spec, operations):
        paths = {}
        for api in operations:
            paths[api[0]] = {
                'operationId': str(spec.__name__) + "." + api[0],
                'summary': api[1].summary.strip(),
                'description': api[1].description.strip(),
                'parameters': self.__get_params(api[1]),
            }
            print("Body Params: ", api[1].body_params)
            if api[1].body_params:
                paths[api[0]]["requestBody"] = self.__get_request_body(api[1])

            paths[api[0]]["responses"] = self.__get_responses(api[1])
        return paths
        
    def __detect_content_from_type(self, val) -> (str, bool, str):
        if val.type == "file":
            return "file", False, val.itype
        if val.type in get_schemas().keys():
            return val.type, True, None
    
        return val.type, False, None

    def __get_params(self, path_spec):
        params = []
        allps = sorted(path_spec.path_params.values(), key=lambda x: x.order) + \
            sorted(path_spec.header_params.values(), key=lambda x: x.order) + \
            sorted(path_spec.query_params.values(), key=lambda x: x.order) + \
            sorted(path_spec.cookie_params.values(),
                   key=lambda x: x.order)  # + \
        # [path_spec.body_param] body param
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

    def __get_request_body(self, path_spec):
        contents = {}
        if path_spec.body_params:
            files_detected = 0  #content = file:xxxx default text/plain
            form_data_detected = 0 #application/x-www-form-urlencoded
            models_detected = 0 #application/json or application/xml

            for (name, val) in path_spec.body_params.items():
                content, ismodel, ftype = self.__detect_content_from_type(val)
                print(content, ismodel, ftype)
                if ftype is not None:
                    files_detected += 1
                elif ismodel:
                    models_detected += 1
                else:
                    form_data_detected += 1

            ctype = ''
            if form_data_detected > 0 and not files_detected and not models_detected:
                ctype = 'application/x-www-form-urlencoded'
                contents[ctype] = {
                    "schema": {
                        "properties": {
                            spec.name: self.__get_real_type(spec.type)['schema'] for spec in path_spec.body_params.values()
                        }
                    }
                }
            elif files_detected == 1 and not form_data_detected and not models_detected:
                f = list(path_spec.body_params.values())[0]
                contents[f.itype] = {
                    "schema": {
                        "type": "string",
                        "format": "binary"  #TODO: When to use byte/base64?
                    }
                }
            elif (files_detected > 0 and (form_data_detected > 0 or models_detected > 0)) or models_detected > 1:
                contents["multipart/form-data"] = {
                    "schema": {
                        "properties": {
                            spec.name: self.__get_real_type(spec.type)['schema'] for spec in path_spec.body_params.values()
                        }
                    }
                }
            elif models_detected == 1 and not files_detected and not form_data_detected:
                f = list(path_spec.body_params.values())[0]
                t = f.itype or 'application/json'
                contents[t] = self.__get_type(f)
            else:
                ctype = 'Unknown'

        return {"content": contents}
            
        

       

    def __get_responses(self, path_spec):
        params = {}
        allresps = sorted(path_spec.responses.values(), key=lambda x: x.name)
        for param in allresps:
            if param:
                params[param.name] = {
                    "description": param.description,
                    "content":
                        # should return default produces if none, otherwise detect from type
                        self._detect_content(param)
                }

                # TODO: implement examples
        return params

    def _detect_content(self, param):

        if param.type not in ('integer', 'int', 'string', 'str', 'boolean', 'bool', 'number', 'int32', 'int64',
                              'float', 'double', "byte", "binary", "date", "date-time", "password"):
            if param.type == "array":
                return {"application/json": {
                    "schema": {
                        "type": "array",
                        # TODO: apply refs
                        "items": self.__get_real_type(param.itype)["schema"]
                    }}
                }

            return {"application/json": self.__get_real_type(param.type)}
        # TODO: other media types
        return {
            "text/plain": {
                "schema": {
                    "type": param.type
                }
            }
        }

    def __get_real_type(self, typestr, **kwargs):
        if typestr in ("int", "integer", "int32"):
            val = {
                "type": "integer",
                "format": "int32"
            }

        elif typestr in ("long", "int64"):
            val = {
                "type": "integer",
                "format": "int64"
            }

        elif typestr in ("float", "double"):
            val = {
                "type": "number",
                "format": typestr
            }

        elif typestr in ("byte", "binary", "date", "password"):
            val = {
                "type": "string",
                "format": typestr
            }

        elif typestr in ("dateTime", "date-time"):
            val = {
                "type": "string",
                "format": "date-time"
            }

        elif typestr in ("str", "string"):
            val = {
                "type": "string"
            }

        elif typestr in ("bool", "boolean"):
            val = {
                "type": "boolean"
            }

        elif is_defined_schema(typestr):
            val = {
                "$ref": "#/components/schemas/" + typestr
            }

        elif typestr == "file":
            val = {
                "type": "string",
                "format": "binary",
            }
        else:
            val = {
                "type": typestr
            }

        val.update(kwargs)
        return {"schema": val}
        # TODO check if typestr is a reference

    def __get_type(self, param):
        if param.type == "array":
            val =  { "type": "array",
                     "items": {
                         "type": param.itype  # TODO detect type
                     }
                   }
            val.update(param.kwargs)
            return {"schema": val}
        if isinstance(param.itype, dict):
            val = {
                "type": param.type
            }
            val.update(param.itype)
            return {"schema": val}
        real_type = self.__get_real_type(
            str(param.type).strip(), **param.kwargs)
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
