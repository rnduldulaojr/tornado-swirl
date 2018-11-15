#pylint: disable=all
import tornado_swirl.swagger as swirl
import tornado_swirl.settings as settings
from tornado_swirl import api_routes
from tornado.testing import AsyncHTTPTestCase, gen_test
from tornado.web import RequestHandler
import json


class TestSampleEndpoints(AsyncHTTPTestCase):

    def setUp(self):
        super(TestSampleEndpoints, self).setUp()
        settings._API_HANDLERS = []
        settings._SCHEMAS = {}
        settings._ROUTES = []

    def get_app(self):
        #print("Returning new app")
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
        }


    @gen_test
    def test_simple_1(self):

        @swirl.restapi('/test')
        class HandlerTest(RequestHandler):
            def get(self):
                """This is a simple test get.

                This is a simple description.

                Query Parameters:
                    foo (string) -- Optional. Simple query string.

                Response:
                    out (string) -- An output.
                """
                self.finish()

        self._app.add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body.decode('utf-8'))
        assert obj['paths']
        assert obj['paths']['/test']
        assert obj['paths']['/test']['get']

        obj = obj['paths']['/test']['get']
        assert obj['responses']
        assert obj['responses']['200']
        assert obj['responses']['200']['description'] == 'An output.'
        assert obj['responses']['200']['content']['text/plain']['schema']
        assert obj['responses']['200']['content']['text/plain']['schema']['type'] == 'string'

    @gen_test
    def test_simple_2(self):

        @swirl.restapi(r'/test/(?P<a>\w+)/(?P<b>\d+)')
        class HandlerTest(RequestHandler):
            def post(self, a, b):
                """This is a simple test get.

                This is a simple description.

                Path Parameters:
                    a (string) -- The a.
                    b (integer) -- The b

                Response:
                    out (string) -- An output.

                Errors:
                    400 -- Bad Request
                    404 -- Not Found
                """
                self.finish()

        self.get_app().add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body.decode('utf-8'))

        assert obj['paths']
        assert obj['paths']['/test/{a}/{b}']
        assert obj['paths']['/test/{a}/{b}']['post']

        obj = obj['paths']['/test/{a}/{b}']['post']
        assert obj['responses']['400']
        assert obj['responses']['404']

    @gen_test
    def test_simple_3(self):

        @swirl.restapi(r'/test/(?P<a>\w+)/(?P<b>\d+)')
        class HandlerTest(RequestHandler):
            def post(self, a, b):
                """This is a simple test get.

                This is a simple description.

                Path Parameters:
                    a (string) -- The a.
                    b (integer) -- The b

                Response:
                    out (Model) -- An output.

                Errors:
                    400 -- Bad Request
                    404 -- Not Found
                """
                self.finish()

        @swirl.schema
        class Model(object):
            """This is a sample model.

            Foo Bar description.

            Properties:
                name (string): Foo name
                type (enum[foo, bar]) : Foo type
            """
            pass

        self.get_app().add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body.decode('utf-8'))
        print(response.body.decode('utf-8'))

        assert obj['paths']
        assert obj['paths']['/test/{a}/{b}']
        assert obj['paths']['/test/{a}/{b}']['post']
        assert obj['components']
        assert obj['components']['schemas']
        assert obj['components']['schemas']['Model']

        obj = obj['paths']['/test/{a}/{b}']['post']
        assert obj['responses']['400']
        assert obj['responses']['404']

    @gen_test
    def test_request_body_form_data(self):
        @swirl.restapi(r'/test/form')
        class HandlerTest(RequestHandler):
            def post(self, a, b):
                """This is a simple test post with form data.

                This is a simple description.

                Request Body:
                    a (string) -- The a.
                    b (integer) -- The b

                Response:
                    out (string) -- An output.

                Errors:
                    400 -- Bad Request
                    404 -- Not Found
                """
                self.finish()

        self.get_app().add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body.decode('utf-8'))
        assert obj['paths']
        assert obj['paths']['/test/form']
        assert obj['paths']['/test/form']['post']
        assert obj['paths']['/test/form']['post']['requestBody']
        assert obj['paths']['/test/form']['post']['requestBody']['content']
        assert obj['paths']['/test/form']['post']['requestBody']['content']['application/x-www-form-urlencoded']

    @gen_test
    def test_request_body_file_data(self):
        @swirl.restapi(r'/test/form')
        class HandlerTest(RequestHandler):
            def post(self, a, b):
                """This is a simple test post with form data.

                This is a simple description.

                Request Body:
                    file (file:text/csv) -- The file.


                Returns:
                    out (string) -- An output.

                Errors:
                    400 -- Bad Request
                    404 -- Not Found
                """
                self.finish()

        self.get_app().add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body.decode('utf-8'))

        assert obj['paths']
        assert obj['paths']['/test/form']
        assert obj['paths']['/test/form']['post']
        assert obj['paths']['/test/form']['post']['requestBody']
        assert obj['paths']['/test/form']['post']['requestBody']['content']
        assert obj['paths']['/test/form']['post']['requestBody']['content']['text/csv']

    @gen_test
    def test_request_body_model(self):
        @swirl.restapi(r'/test/form')
        class HandlerTest(RequestHandler):
            def post(self, a, b):
                """This is a simple test post with form data.

                This is a simple description.

                Request Body:
                    user (Model) -- Model model.


                Response:
                    out (string) -- An output.

                Errors:
                    400 -- Bad Request
                    404 -- Not Found
                """
                self.finish()

        @swirl.schema
        class Model(object):
            """This is a sample model.

            Foo Bar description.

            Properties:
                name (string): Foo name
                type (enum[foo, bar]) : Foo type
            """
            pass

        self.get_app().add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body.decode('utf-8'))
        assert obj['paths']
        assert obj['paths']['/test/form']
        assert obj['paths']['/test/form']['post']
        assert obj['paths']['/test/form']['post']['requestBody']
        assert obj['paths']['/test/form']['post']['requestBody']['content']
        assert obj['paths']['/test/form']['post']['requestBody']['content']['application/json']

    @gen_test
    def test_simple_descriptions(self):

        @swirl.restapi('/test')
        class HandlerTest(RequestHandler):
            def get(self):
                """This is a simple test get.

                This is a simple description.

                Query Parameters:
                    foo (string) -- Optional. Simple query string.
                        example: bar

                Response:
                    out (string) -- An output.
                        example: foo
                """
                self.finish()

        self.get_app().add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body.decode('utf-8'))
        assert obj['paths']
        assert obj['paths']['/test']
        assert obj['paths']['/test']['get']

        obj = obj['paths']['/test']['get']
        assert obj['responses']
        assert obj['responses']['200']
        assert obj['responses']['200']['description'] == 'An output.'
        assert obj['responses']['200']['content']['text/plain']['schema']
        assert obj['responses']['200']['content']['text/plain']['schema']['type'] == 'string'
        assert obj['responses']['200']['content']['text/plain']['schema']['example'] == 'foo'

    @gen_test
    def test_simple_parse_with_multipart_request_body(self):

        @swirl.restapi("/test")
        class Handler(RequestHandler):

            def post():
                """This is the simple description.
                With a second line.

                Long description.
                With a second line.

                Request Body:
                    file (file:image/png) -- Required.  Image file.
                    name (string) -- Required.  Name.
            """
            pass

        self.get_app().add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body.decode('utf-8'))

        assert obj['paths']
        assert obj['paths']['/test']
        assert obj['paths']['/test']['post']
        assert obj['paths']['/test']['post']['requestBody']
        assert obj['paths']['/test']['post']['requestBody']['content']
        assert obj['paths']['/test']['post']['requestBody']['content']["multipart/form-data"]

    @gen_test
    def test_describe_1(self):
        self.reset_settings()
        swirl.describe(title='title', description='description', servers=[
            {'url': 'http://test/', 'description': 'test', 'foo': 'foo'}
        ])

        @swirl.restapi("/test")
        class Handler(RequestHandler):

            def post():
                """This is the simple description.
                With a second line.

                Long description.
                With a second line.

                Request Body:
                    file (file:image/png) -- Required.  Image file.
                    name (string) -- Required.  Name.
            """
            pass

        self._app.add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body.decode('utf-8'))
        assert obj.get("openapi", None) == "3.0.0"
        assert obj["info"]
        assert obj["info"]["title"]
        assert obj["info"]["title"] == "title"
        assert obj["info"]["description"]
        assert obj["info"]["description"] == "description"

        assert obj["servers"]
        assert len(obj["servers"]) == 1
        assert obj["servers"][0]
        assert obj["servers"][0]["url"]
        assert obj["servers"][0]["url"] == "http://test/"

        assert obj["servers"][0].get("foo") is None

    @gen_test
    def test_describe_2_default_server(self):
        # reset default_settings
        self.reset_settings()
        swirl.describe(title='title', description='description')
        @swirl.restapi("/test")
        class Handler(RequestHandler):

            def post():
                """This is the simple description.
                With a second line.

                Long description.
                With a second line.

                Request Body:
                    file (file:image/png) -- Required.  Image file.
                    name (string) -- Required.  Name.
            """
            pass

        self._app.add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body.decode('utf-8'))
        print(obj)
        assert obj.get("openapi", None) == "3.0.0"
        assert obj["info"]
        assert obj["info"]["title"]
        assert obj["info"]["title"] == "title"
        assert obj["info"]["description"]
        assert obj["info"]["description"] == "description"

        assert obj["servers"]
        assert len(obj["servers"]) == 1
        assert obj["servers"][0]
        assert obj["servers"][0]["url"]
        assert obj["servers"][0]["description"]
        assert obj["servers"][0]["description"] == "Default server"


    @gen_test
    def test_simple_parse_with_urlencoded_request_body(self):

        @swirl.restapi("/test")
        class Handler(RequestHandler):

            def post():
                """This is the simple description.
                With a second line.

                Long description.
                With a second line.

                Request Body:
                    foo  (string) -- Required.  Image file.
                    name (string) -- Required.  Name.
            """
            pass

        self.get_app().add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body.decode('utf-8'))

        assert obj['paths']
        assert obj['paths']['/test']
        assert obj['paths']['/test']['post']
        assert obj['paths']['/test']['post']['requestBody']
        assert obj['paths']['/test']['post']['requestBody']['content']
        assert obj['paths']['/test']['post']['requestBody']['content']["application/x-www-form-urlencoded"]


    @gen_test
    def test_spec_html(self):
        @swirl.restapi("/test")
        class Handler(RequestHandler):

            def post():
                """This is the simple description.
                With a second line.

                Long description.
                With a second line.

                Request Body:
                    foo  (string) -- Required.  Image file.
                    name (string) -- Required.  Name.
            """
            pass

        self.get_app().add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec.html'))
        assert response.code == 200

