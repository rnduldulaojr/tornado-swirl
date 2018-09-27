from tornado_swirl.swagger import restapi, Application
from tornado_swirl import api_routes
import tornado.web
import tornado.ioloop

@restapi(url="/test") 
class MainHandler(tornado.web.RequestHandler):
    """Foo"""

    async def get(self):
        """Test summary

        Test description

        Query Params:
            param1 (int) -- test
        """
        self.finish()

@restapi("/test/(?P<emp_uid>\d+)/(?P<date>[\w-]+)")
class TestHandler(tornado.web.RequestHandler):
    """Mother ship"""

    async def get(self, emp_uid, date):
        """Test get

        Hiho

        Cookie:
            x (string) -- some foo

        Path Params:
            emp_uid (int) -- test
            date ([string]) -- test
        """
        self.finish()

@restapi('/item/(?P<itemid>\d+)')
class ItemHandler(tornado.web.RequestHandler):

    def get(self, itemid):
        """Get Item data.

        Gets Item data from database.

        Path Parameter:
            itemid (int) -- The item id
        """
        pass

def make_app():
    return Application(api_routes())

if __name__ == "__main__":
    app = make_app()
    app.debug = True
    app.autoreload = True
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()