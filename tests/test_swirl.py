#pylint: disable=all
import tornado_swirl.swagger as swirl
import tornado_swirl.settings as settings
from tornado_swirl import api_routes
from tornado.testing import  AsyncHTTPTestCase, gen_test
from tornado.web import RequestHandler
import json


class TestSampleEndpoints(AsyncHTTPTestCase):

    def setUp(self):
        super().setUp()
        settings._API_HANDLERS = []
        settings._SCHEMAS = {}
        settings._ROUTES = []

    def get_app(self):
        return swirl.Application()


    @gen_test
    def test_simple_1(self):
        
        @swirl.restapi('/test')
        class HandlerTest(RequestHandler):
            async def get(self):
                """This is a simple test get.

                This is a simple description.

                Query Parameters:
                    foo (string) -- Optional. Simple query string.
                
                Response:
                    out (string) -- An output.
                """
                self.finish()

        self.get_app().add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body)
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
            async def post(self, a, b):
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
        obj = json.loads(response.body)

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
            async def post(self, a, b):
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
        obj = json.loads(response.body)

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
            async def post(self, a, b):
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
        obj = json.loads(response.body)
        print(response.body)
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
            async def post(self, a, b):
                """This is a simple test post with form data.

                This is a simple description.

                Request Body:
                    file (file:text/csv) -- The file.
                    
                
                Response:
                    out (string) -- An output.

                Errors:
                    400 -- Bad Request
                    404 -- Not Found
                """
                self.finish()

        self.get_app().add_handlers(r".*", api_routes())
        response = yield self.http_client.fetch(self.get_url('/swagger/spec'))
        obj = json.loads(response.body)
        print(response.body)
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
            async def post(self, a, b):
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
        obj = json.loads(response.body)
        print(response.body)
        assert obj['paths']
        assert obj['paths']['/test/form']
        assert obj['paths']['/test/form']['post']
        assert obj['paths']['/test/form']['post']['requestBody']
        assert obj['paths']['/test/form']['post']['requestBody']['content']
        assert obj['paths']['/test/form']['post']['requestBody']['content']['application/json']