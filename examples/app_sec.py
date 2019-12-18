from tornado_swirl.swagger import restapi, schema, Application, describe
from tornado_swirl import api_routes, add_security_scheme
import tornado.web
import tornado.ioloop
from tornado_swirl.openapi import security

describe(title='Test API', description='Just things to test')

#setup security scheme
scheme1 = security.HTTP('basic')

add_security_scheme('basic_scheme', scheme1)

@restapi('/path/to/api')
class MyHandler(tornado.web.RequestHandler):
    async def get(self):
        """This will be the API path summary.

        While the long description will be the API description.

        Query Parameters:
            date (date) -- Required.  The target date.
            sort (enum[asc, desc]) -- Optional.  Sort order. 
            items (int) -- Optional.  Number of items to display.
                minimum: 100    maximum: 200
        
        Returns:
            items ([string]) -- List of random strings.
        
        Error Responses:
            400 (ErrorResponse) -- Bad Request.
            500 (ErrorResponse) -- Internal Server Error.

        Tags:
            internal

        Security:
            basic_scheme
        """
        self.finish()


@schema
class ErrorResponse(object):
    """Error response object.

    Properties:
        code (int) -- Required.  Error code.
        message (string) -- Error description.
    """
    pass

def make_app():
    return Application(api_routes(), autoreload=True)

if __name__ == "__main__":
    app = make_app()
    app.debug = True
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()