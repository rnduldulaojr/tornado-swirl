# -*- coding: utf-8 -*-
"""Swirl Settings module."""
import os.path

__author__ = 'rduldulao'

SWAGGER_VERSION = '3.0.0'

URL_SWAGGER_API_DOCS = 'swagger-api-docs'
URL_SWAGGER_API_LIST = 'swagger-api-list'
URL_SWAGGER_API_SPEC = 'swagger-api-spec'

STATIC_PATH = os.path.join(os.path.dirname(os.path.normpath(__file__)), 'static')

default_settings = {
    'static_path': STATIC_PATH,
    'swagger_prefix': '/swagger',
    'api_version': 'v1.0',
    'title': 'Sample API',
    'description': 'Sample description',
    'servers': [],
    'api_key': '',
    'enabled_methods': ['get', 'post', 'put', 'patch', 'delete'],
    'exclude_namespaces': [],
    'tags': [],
}

class SwirlVars(object):
    """Container for swirl handler vars"""
    SCHEMAS = dict()
    ROUTES = []
    API_HANDLERS = []
    GLOBAL_TAGS = []

def get_api_handlers():
    """Returns REST API handlers"""
    return SwirlVars.API_HANDLERS

def add_global_tag(name, description=None, url=None):
    tag = {}
    tag['name'] = name
    if description:
        tag['description'] = description
    
    if url:
        tag['externalDocs'] = { 'url': url }
    SwirlVars.GLOBAL_TAGS.append(tag)

def add_api_handler(cls):
    """Adds a REST API handler class"""
    SwirlVars.API_HANDLERS.append(cls)

def add_route(path, handler, **kwargs):
    """Add a REST API route."""
    SwirlVars.ROUTES.append((path, handler, kwargs))

def api_routes():
    """Return all registered REST API routes via @restapi decorator"""
    return SwirlVars.ROUTES

def get_schemas():
    """Return all registered REST API models via @schema decorator"""
    return SwirlVars.SCHEMAS

def is_defined_schema(name):
    """Returns True if named schema is registered."""
    return True if SwirlVars.SCHEMAS.get(name) else False

def add_schema(name, cls):
    """Add a schema"""
    SwirlVars.SCHEMAS[name] = cls
