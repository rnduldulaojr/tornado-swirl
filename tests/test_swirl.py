import tornado_swirl.swagger as swirl
from tornado_swirl import api_routes
from tornado.testing import  AsyncHTTPTestCase, gen_test
from tornado.web import RequestHandler
import json


class TestSampleEndpoints(AsyncHTTPTestCase):

    #def setUp(self):
        #reset the caches
    #    pass

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
                self.finish

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
