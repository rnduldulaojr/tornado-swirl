# tornado-swirl

## What is tornado-swirl?
Tornado-swirl is a wrapper for tornado which enables swagger-ui support, adapted from Serena Feng's tornado-swagger project and then
heavily modified to work with Tornado 5 and Python 3 and uses Google-style docstrings to get OpenAPI 2.0 API path descriptors.  

Parameters(query, path, cookie, header, request body) need to be specified in their own sections and each parameter is described as follows:

```
name (type) -- (required?) description
```

```type``` and ```required```  (which can be "Required." or "Optional.") as well as ```description``` can be optional.  

Example docstring:


```python
"""This will become the path summary.

This will become the path description which should be longer than the
summary and can span multiple lines.

Headers:
    Authentication (string) -- Required.  Bearer token.
    Content-Type -- Optional.  The content type of the request body.

Query Parameters:
    start_time (integer) -- The start timestamp.
    ids ([string]) -- Array of user ids.

Request Body:
    data (json) -- The data on the body

Returns:
    items (json) -- The item data.

Errors:
    404 -- {"code": 404, "message": "Not Found"}.

"""
```

[THIS IS A WORK IN PROGRESS, comments/criticisms are welcome.]


## Installation
TODO:

## Documenting your Handlers

Swirl uses the ```restapi``` decorator to get both the routing info AND the swagger spec which is derived from the method module docs.

```python
import tornado.web

import tornado_swirl as swirl
from tornado_swirl import restapi, api_routes

@restapi('/item/(?P<itemid>\d+)')
class ItemHandler(tornado.web.RequestHandler):

    def get(self, itemid):
        """Get Item data.

        Gets Item data from database.

        Path Parameter:
            itemid (int) -- The item id
        """
        pass

# Then you use swagger.Application instead of tornado.web.Application
# and do other operations as usual

def make_app():
    return swirl.Application(api_routes())

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
```
TODO: Models/Components

# Running and testing

Now run your tornado app

```
python app.py
```

And visit:

```
curl http://localhost:8888/swagger/spec
```

Swagger spec will look something like:

```json
{
    "apiVersion": "v1.0",
    "swagger": "2.0",
    "basePath": "http://localhost:8888/",
    "schemes": [
        "http",
        "https"
    ],
    "consumes": [
        "application/json"
    ],
    "produces": [
        "application/json"
    ],
    "paths": [
        {
            "/item/{itemid}": {
                "get": {
                    "operationId": "ItemHandler.get",
                    "summary": "Get Item data.",
                    "description": "Gets Item data from database.",
                    "parameters": [
                        {
                            "in": "path",
                            "name": "itemid",
                            "schema": {
                                "type": "int"
                            },
                            "required": true,
                            "description": "The item id"
                        }
                    ]
                }
            }
        }
    ]
}


```
