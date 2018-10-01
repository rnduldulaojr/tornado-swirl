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
    'base_url': '/',
    'static_path': STATIC_PATH,
    'swagger_prefix': '/swagger',
    'api_version': 'v1.0',
    'api_key': '',
    'enabled_methods': ['get', 'post', 'put', 'patch', 'delete'],
    'exclude_namespaces': [],
}

_SCHEMAS = dict()

_ROUTES = []

_API_HANDLERS = []

def get_api_handlers() -> list:
    """Returns REST API handlers"""
    return _API_HANDLERS

def add_api_handler(cls):
    """Adds a REST API handler class"""
    _API_HANDLERS.append(cls)

def add_route(path, handler,  **kwargs):
    """Add a REST API route."""
    _ROUTES.append((path, handler, kwargs))

def api_routes():
    """Return all registered REST API routes via @restapi decorator"""
    return _ROUTES

def get_schemas() -> dict:
    """Return all registered REST API models via @schema decorator"""
    return _SCHEMAS

def is_defined_schema(name):
    """Returns True if named schema is registered."""
    global _SCHEMAS
    return True if _SCHEMAS.get(name) else False

def add_schema(name, cls):
    """Add a schema"""
    global _SCHEMAS 
    _SCHEMAS[name] = cls
