# -*- coding: utf-8 -*-
"""
Swagger handler utils
"""

from tornado.web import StaticFileHandler, URLSpec

from tornado_swirl.views import (SwaggerApiHandler, #SwaggerResourcesHandler,
                                 SwaggerUIHandler)

from .settings import (URL_SWAGGER_API_DOCS, #URL_SWAGGER_API_LIST,
                       URL_SWAGGER_API_SPEC, default_settings)

__author__ = 'rduldulao'


def swagger_handlers():
    """Returns the swagger UI handlers

    Returns:
        [(route, handler)] -- list of Tornado URLSpec
    """

    prefix = default_settings.get('swagger_prefix', '/swagger')
    if prefix[-1] != '/':
        prefix += '/'
    return [
        URLSpec(prefix + r'spec.html$', SwaggerUIHandler,
                default_settings, name=URL_SWAGGER_API_DOCS),
        # URLSpec(prefix + r'spec.json$', SwaggerResourcesHandler,
        #         default_settings, name=URL_SWAGGER_API_LIST),
        URLSpec(prefix + r'spec$', SwaggerApiHandler,
                default_settings, name=URL_SWAGGER_API_SPEC),
        (prefix + r'(.*\.(css|png|gif|js))', StaticFileHandler,
         {'path': default_settings.get('static_path')}),
    ]
