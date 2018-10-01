from tornado_swirl.swagger import restapi, schema, Application
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
            param1 (integer) -- required. test
                minimum: 1  maximum: 200  exclusiveMaximum: true

        Response:
            x (enum[a,b,c]) -- Foomanchu
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
            date (enum[a,b,c]) -- test

        200 Response:
            test ([User]) -- Test data
        
        201 Response:
            test (User) -- Test user
        
        Error Response:
            400  -- Fudge
        """
        self.finish()

@restapi('/item/(?P<itemid>\d+)')
class ItemHandler(tornado.web.RequestHandler):

    def get(self, itemid):
        """Get Item data.

        Gets Item data from database.

        Path Parameter:
            itemid (integer) -- The item id
        """
        pass

@restapi('/withrequestbody')
class FooHandler(tornado.web.RequestHandler):

    def get(self, itemid):
        """Get Item data.

        Gets Item data from database.

        Request Body:
            itemid (integer) -- The item id
        """
        pass


@restapi('/withrequestbody2')
class FooHandler2(tornado.web.RequestHandler):

    def get(self, itemid):
        """Get Item data.

        Gets Item data from database.

        Request Body:
            file (file:text/csv) -- CSV file.
        """
        pass

@restapi('/withrequestbody3')
class FooHandler3(tornado.web.RequestHandler):

    def get(self, itemid):
        """Get Item data.

        Gets Item data from database.

        Request Body:
            file (file:text/csv) -- CSV file.
            name (string) -- required. Foo name.
        """
        pass

@restapi('/withrequestbody4')
class FooHandler4(tornado.web.RequestHandler):

    def get(self, itemid):
        """Get Item data.

        Gets Item data from database.

        Request Body:
            file (file:text/csv) -- CSV file.
            name (string) -- required. Foo name.
            user (User) -- required. User data.
        """
        pass

@restapi('/withrequestbody5')
class FooHandler5(tornado.web.RequestHandler):

    def get(self, itemid):
        """Get Item data.

        Gets Item data from database.

        Request Body:
            user (User) -- required. User data.
        """
        pass

@schema
class User(object):
    """User 

    User def

    Properties:
        name (string) -- required. The name
        age (int) -- The age.
            minimum: 1  maximum: 100
    """
    pass

def make_app():
    return Application(api_routes(), autoreload=True)

if __name__ == "__main__":
    app = make_app()
    app.debug = True
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()