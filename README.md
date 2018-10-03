# tornado-swirl

## What is tornado-swirl?
Tornado-swirl is a wrapper for tornado which enables swagger-ui support, adapted from Serena Feng's tornado-swagger project and then
heavily modified to work with Tornado 5 and Python 3 and uses Google-style docstrings to get OpenAPI 3.0 API path descriptors.  

Parameters(query, path, cookie, header, request body) need to be specified in their own sections and each parameter is described as follows:

```
name (type) -- (required?) description
```

OR they can have OpenAPI 3.0 schema properties:

```
age (int) -- (optional) Age of person.
    minimum: 0  maximum: 150
```

```type``` and ```required```  (which can be "Required." or "Optional.") as well as ```description``` can be optional.  

### Example docstring:


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

### Example Schema Docstring

```python
"""
The User class.

User from database.

Properties:
    name (string) -- Required.  User full name.
    age (int) -- User's age.
        minimum: 1   maximum: 100
"""

```

[THIS IS A WORK IN PROGRESS, comments/criticisms are welcome.]


## Installation
TODO:

## Documenting your Handlers and Models/Schemas

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

@schema
class User(object):
    """This is the user class

    Your usual long description.

    Properties:
        name (string) -- required.  Name of user
        age (int) -- Age of user

    """
    pass



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

Or you can view via Swagger UI in your browser:

```
http://localhost:8888/swagger/spec.html
```

Swagger spec will look something like:

```json
{
    "openapi": "3.0.0",
    "info": {
        "title": "Sample API",
        "description": "Foo bar",
        "version": "v1.0"
    },
    "servers": [
        {
            "url": "http://localhost:8888/",
            "description": "This server"
        }
    ],
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
    "paths": {
        "/test": {
            "get": {
                "operationId": "MainHandler.get",
                "summary": "Test summary",
                "description": "Test description",
                "parameters": [
                    {
                        "in": "query",
                        "name": "param1",
                        "required": true,
                        "description": "test",
                        "schema": {
                            "type": "integer",
                            "format": "int32",
                            "maximum": 200,
                            "minimum": 1
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Foomanchu",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "type": "string"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        },
        "/test/{emp_uid}/{date}": {
            "get": {
                "operationId": "TestHandler.get",
                "summary": "Test get",
                "description": "Hiho",
                "parameters": [
                    {
                        "in": "path",
                        "name": "emp_uid",
                        "required": true,
                        "description": "test",
                        "schema": {
                            "type": "integer",
                            "format": "int32"
                        }
                    },
                    {
                        "in": "path",
                        "name": "date",
                        "required": true,
                        "description": "test",
                        "schema": {
                            "type": "string",
                            "format": "date"
                        }
                    },
                    {
                        "in": "cookie",
                        "name": "x",
                        "required": false,
                        "description": "some foo",
                        "schema": {
                            "type": "string"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "Test data",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": "array",
                                    "items": {
                                        "$ref": "#/components/schemas/User"
                                    }
                                }
                            }
                        }
                    },
                    "201": {
                        "description": "Test user",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "$ref": "#/components/schemas/User"
                                }
                            }
                        }
                    },
                    "400": {
                        "description": "Fudge",
                        "content": {
                            "application/json": {
                                "schema": {
                                    "type": null
                                }
                            }
                        }
                    }
                }
            }
        },
        "/item/{itemid}": {
            "get": {
                "operationId": "ItemHandler.get",
                "summary": "Get Item data.",
                "description": "Gets Item data from database.",
                "parameters": [
                    {
                        "in": "path",
                        "name": "itemid",
                        "required": true,
                        "description": "The item id",
                        "schema": {
                            "type": "integer",
                            "format": "int32"
                        }
                    }
                ],
                "responses": {}
            }
        }
    },
    "components": {
        "schemas": {
            "User": {
                "type": "object",
                "required": [
                    "name"
                ],
                "properties": {
                    "name": {
                        "type": "string"
                    },
                    "age": {
                        "type": "integer",
                        "format": "int32",
                        "maximum": 100,
                        "minimum": 1
                    }
                }
            }
        }
    }
}


```

## Credits to:

We used SerenaFeng's [tornado-swagger](https://github.com/SerenaFeng/tornado-swagger) as starting point for this project.

We decided on (almost like) Google style module docs for the doc format since epydoc used in tornado-swagger has been a discontinued project and
did not work on Python 3.  We wanted to maintain a uniform python docstring format across all our projects so we decided on extracting OpenAPI 3.0 
data from our existing/common docstring format so we made our own parser based on [Brian Ray's Medium article on FSMs](https://medium.com/@brianray_7981/tutorial-write-a-finite-state-machine-to-parse-a-custom-language-in-pure-python-1c11ade9bd43). 