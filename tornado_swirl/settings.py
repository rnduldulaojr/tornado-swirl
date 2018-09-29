# -*- coding: utf-8 -*-
import os.path

__author__ = 'rduldulao'

SWAGGER_VERSION = '3.0.0'

URL_SWAGGER_API_DOCS = 'swagger-api-docs'
URL_SWAGGER_API_LIST = 'swagger-api-list'
URL_SWAGGER_API_SPEC = 'swagger-api-spec'

STATIC_PATH = os.path.join(os.path.dirname(os.path.normpath(__file__)), 'static')

default_settings = {
    'base_url': '/',
    'static_path': STATIC_PATH,
    'swagger_prefix': '/swagger',
    'api_version': 'v1.0',
    'api_key': '',
    'enabled_methods': ['get', 'post', 'put', 'patch', 'delete'],
    'exclude_namespaces': [],
}

_SCHEMAS = {}

_ROUTES = []

_API_HANDLERS = []

def get_api_handlers() -> list:
    return _API_HANDLERS

def add_api_handler(cls):
    _API_HANDLERS.append(cls)

def add_route(path, handler,  **kwargs):
    _ROUTES.append((path, handler, kwargs))

def api_routes():
    return _ROUTES

def get_schemas() -> dict:
    return _SCHEMAS

def is_defined_schema(name):
    global _SCHEMAS
    return True if _SCHEMAS.get(name) else False

def add_schema(name, cls):
    global _SCHEMAS
    _SCHEMAS[name] = cls
