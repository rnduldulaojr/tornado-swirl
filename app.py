import tornado.ioloop
import tornado.web
from tornado.gen import coroutine

from tornado_swirl import api_routes
from tornado_swirl.swagger import Application, describe, restapi, schema, add_global_tag, add_security_scheme
from tornado_swirl.openapi import security


describe(title='Test API', description='Just things to test',
         swagger_ui_handlers_headers=[
             ('Cache-Control', 'public'),
             ('Cache-Control', 'max-age=300')
         ])
add_global_tag("internal", "Internal Use Only", "http://foo.com/tags")
add_security_scheme("test_api_key", security.HTTP('bearer', 'JWT'))
add_security_scheme("api_key", security.APIKey('X-API-KEY'))

# @restapi(url="/test")
# class MainHandler(tornado.web.RequestHandler):
#     """Foo"""

#     async def get(self):
#         """Test summary

#         Test description

#         Query Params:
#             param1 (integer) -- required. test
#                 minimum: 1  maximum: 200  exclusiveMaximum: true

#         Response:
#             x (enum[a,b,c]) -- Foomanchu
#         """
#         self.finish()

# @restapi("/test/(?P<emp_uid>\d+)/(?P<date>[\w-]+)")
# class TestHandler(tornado.web.RequestHandler):
#     """Mother ship"""

#     async def get(self, emp_uid, date):
#         """Test get

#         Hiho

#         Cookie:
#             x (string) -- some foo

#         Path Params:
#             emp_uid (int) -- test
#             date (enum[a,b,c]) -- test

#         200 Response:
#             test ([User]) -- Test data

#         201 Response:
#             test (User) -- Test user

#         Error Response:
#             400  -- Fudge
#         """
#         self.finish()

# @restapi('/item/(?P<itemid>\d+)')
# class ItemHandler(tornado.web.RequestHandler):

#     def get(self, itemid):
#         """Get Item data.

#         Gets Item data from database.

#         Path Parameter:
#             itemid (integer) -- The item id
#         """
#         pass

# @restapi('/withrequestbody')
# class FooHandler(tornado.web.RequestHandler):

#     def get(self, itemid):
#         """Get Item data.

#         Gets Item data from database.

#         Request Body:
#             itemid (integer) -- The item id
#         """
#         pass


# @restapi('/withrequestbody2')
# class FooHandler2(tornado.web.RequestHandler):

#     def get(self, itemid):
#         """Get Item data.

#         Gets Item data from database.

#         Request Body:
#             file (file:text/csv) -- CSV file.
#         """
#         pass

# @restapi('/withrequestbody3')
# class FooHandler3(tornado.web.RequestHandler):

#     def get(self, itemid):
#         """Get Item data.

#         Gets Item data from database.

#         Request Body:
#             file (file:text/csv) -- CSV file.
#             name (string) -- required. Foo name.
#         """
#         pass

@restapi('/chunky')
class FooHandler4(tornado.web.RequestHandler):

    @coroutine
    def get(self):
        self.set_header('Content-Type', 'application/json')
        self.write('{ "data": ')
        self.write('"')
        for i in range(1000):
            
            self.write('foobar')
            yield self.flush()
        self.write('" }')
        yield self.flush()

@restapi('/withrequestbody5')
class FooHandler5(tornado.web.RequestHandler):

    def get(self):
        """Get Item data.

        Gets Item data from database.

        Security:
            api_key --
            test_api_key -- 
        """
        self.finish()

    def post(self):
        """Get Item data.

        Gets Item data from database.

        HTTP Headers: 
            Tt-I2ap-Id -- Uri.
            Tt-I2ap-Sec -- Some Hex token

        Request Body:
            user (object) -- required. User data.
        """
        pass

@restapi('/withrequestbody6')
class FooHandler6(tornado.web.RequestHandler):

    
    def post(self):
        """Create Admin

        Request Body:
            user (Admin) -- required. User data.
        """
        pass

@schema
class User(object):
    """User

    User def

    Properties:
        underscore_test -- Test
        m9_9 -- Test
        name (string) -- required. The name
        age (int) -- The age.
            minimum: 1  maximum: 100
    """
    pass

@schema
class Admin(User):
    """Admin is a User

    Properties:
        superpowers ([string]) -- list of superpowers.
    """
    # class Meta:
    #     examples = {
    #         "Ron": {
    #             "name": "Ronald",
    #             "age": 10,
    #             "superpowers": ["a", "b", "c"]
    #         },
    #         "Don": {
    #             "name": "McDonald",
    #             "age": 12,
    #             "superpowers": ["c", "d", "e"]
    #         }
    #     }
    class Meta:
        example = {
                "name": "Ronald",
                "age": 10,
                "superpowers": ["a", "b", "c"]
            }
    


@restapi('/path/to/api')
class MyHandler(tornado.web.RequestHandler):
    async def get(self):
        """This will be the API path summary.

        While the long description will be the API description.

        Query Parameters:
            date (date) -- Required.  The target date.
            sort (enum[asc, desc, with-params]) -- Optional.  Sort order.
            items (int) -- Optional.  Number of items to display.
                minimum: 100    maximum: 200

        Returns:
            items ([string]) -- List of random strings.

        Error Responses:
            200 (Admin) -- Test Admin.
            400 (ErrorResponse) -- Bad Request.
            500 (ErrorResponse) -- Internal Server Error.

         Tags:
            internal api
        """
        self.finish()


@schema
class ErrorResponse(object):
    """Error response object.

    Properties:
        code (int) -- Required.  Error code.
        message (string) -- Error description.
            readOnly: true
        details (object) -- Object
            minProperties: 2
    """
    class Meta:
        example = {
            "code": 400,
            "message": "Some message",
            "details": {
                "foo": True,
                "bar": False
            }
        }


def make_app():
    return Application(api_routes(), autoreload=True)


if __name__ == "__main__":
    print("Test app")
    app = make_app()
    app.debug = True
    app.listen(8001)
    tornado.ioloop.IOLoop.current().start()
