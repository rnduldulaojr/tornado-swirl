#pylint: disable=all
import tornado_swirl.swagger as swirl
import tornado_swirl.settings as settings
from tornado_swirl import api_routes
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import RequestHandler
import json


class TestSampleEndpoints2(AsyncHTTPTestCase):

    def setUp(self):
        super(TestSampleEndpoints2, self).setUp()
        settings._API_HANDLERS = []
        settings._SCHEMAS = {}
        settings._ROUTES = []

    def get_app(self):
        return swirl.Application()

    def reset_settings(self):
        settings.default_settings = {
            'static_path': settings.STATIC_PATH,
            'swagger_prefix': '/swagger',
            'api_version': 'v1.0',
            'title': 'Sample API',
            'description': 'Sample description',
            'servers': [],
            'api_key': '',
            'enabled_methods': ['get', 'post', 'put', 'patch', 'delete'],
            'exclude_namespaces': [],
            'json_mime_type': 'application/json'
        }
    @gen_test
    def test_simple_1(self):
        self.reset_settings()

        @swirl.restapi('/test')
        class HandlerTest(RequestHandler):
            def get(self):
                """This is a simple test get.

                This is a simple description.

                Query Parameters:
                    foo (string) -- Optional. Simple query string.

                Response:
                    test (B) -- An output.
                """
                self.finish()
        @swirl.schema
        class A(object):
            """Parent class

            Properties:
                name (string) -- Test name.
            """

        @swirl.schema
        class B(A):
            """Sub class

            Properties:
                subname (string) -- Test sub name
            """

        self._app.add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body.decode('utf-8'))
        assert obj['paths']
        assert obj['paths']['/test']
        assert obj['paths']['/test']['get']

        handler = obj['paths']['/test']['get']
        assert handler['responses']
        assert handler['responses']['200']
        assert handler['responses']['200']['description'] == 'An output.'
        assert handler['responses']['200']['content']['application/json']['schema']
        assert handler['responses']['200']['content']['application/json']['schema']['$ref']

        schemas = obj['components']['schemas']
        assert schemas
        assert schemas['A']
        assert schemas['B']
        assert schemas['B']['allOf']
        assert schemas['B']['allOf'][0]
        assert schemas['B']['allOf'][1]
