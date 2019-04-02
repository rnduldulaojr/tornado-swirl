# tornado-swirl

[![CircleCI](https://circleci.com/gh/rduldulao/tornado-swirl.svg?style=svg)](https://circleci.com/gh/rduldulao/tornado-swirl)

## What is tornado-swirl?
Tornado-swirl is a wrapper for tornado which enables swagger-ui support, adapted from Serena Feng's tornado-swagger project and then
heavily modified to work with Tornado 5 and Python 3 and uses Google-style docstrings to get OpenAPI 3.0 API path and component descriptors.  

The main idea for this project is to automatically extract API specs from the usual docstrings of our Tornado RequestHandlers.

Swirl uses the ```@restapi``` decorator to get both the routing info AND the swagger spec which is derived from the method module docs. While ```@schema``` decorator is used to mark classes to include them into the ```components/schemas``` section of the resulting OpenAPI spec.

## Releases:
* V. 0.1.18 -- Added support for ```example```/```examples``` for schema model types, bug fix on enum values with dash, updated swagger UI resources, code cleanup.
* V. 0.1.17 -- Added support for ```object``` (freeform object) type, added support for schema inheritance, and ```json_mime_type``` option in ```swirl.describe(...)``` to enable JSON:API authors to specify ```application/vnd.api+json```.
* V. 0.1.16 -- Added support for OpenAPI ```securityScheme```  and path ```security``` spec.  Support for ```apiKey``` and ```http``` security schemes.
* V. 0.1.15 -- Added swagger_ui_handlers_headers and swagger_spec_headers as ```describe()``` keyword arguments, adding of
               custom response headers for the swagger UI elements and the JSON spec through the said keyword arguments.
* V. 0.1.14 -- Modified handling of enabled_methods, added 'head' to list by default.
* V. 0.1.13 -- Added "Deprecated" to mark deprecated APIs.
* V. 0.1.12 -- Modified parameter naming to allow hypen/underscore digits.
* V. 0.1.11 -- Fixed bug where descriptions are not being included in schema and schema properties.
* V. 0.1.10 -- Lowered Python version requirement to 3.6, Added add_global_tag to tornado_swirl import.
* v. 0.1.8 -- Support `tags` OpenAPI property.  
* v. 0.1.7 -- Fixed bug where multiple host value (comma delimited) appears on ```servers``` value.  Also modified ```swirl.describe``` behavior.
* v. 0.1.5 -- Fixed bug where ```application/json``` response has no ```schema``` attribute.
* v. 0.1.2 -- Fixed openapi package inclusion


[Tutorial and More Details Here](./TUTORIAL.md)

## Quick Look
```python
import tornado.web

import tornado_swirl as swirl

@swirl.restapi('/item/(?P<itemid>\d+)')
class ItemHandler(tornado.web.RequestHandler):

    def get(self, itemid):
        """Get Item data.

        Gets Item data from database.

        Path Parameter:
            itemid (int) -- The item id
        
        Tags:
            items
        """
        pass

@swirl.schema
class User(object):
    """This is the user class

    Your usual long description.

    Properties:
        name (string) -- required.  Name of user
        age (int) -- Age of user

    """
    pass


def make_app():
    return swirl.Application(swirl.api_routes())

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
```
TODO: Models/Components

## Running and testing

Run your app:

```
% python app.py
```

And visit:

```
% curl http://localhost:8888/swagger/spec
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
                "description": "User def",
                "required": [
                    "name"
                ],
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "User name"
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

We decided on (almost like) Google style module docs for the doc format since epydoc used in tornado-swagger has been a discontinued project and did not work on Python 3.  We wanted to maintain a uniform python docstring format across all our projects so we decided on extracting OpenAPI 3.0  data from our existing/common docstring format so we made our own parser based on [Brian Ray's Medium article on FSMs](https://medium.com/@brianray_7981/tutorial-write-a-finite-state-machine-to-parse-a-custom-language-in-pure-python-1c11ade9bd43). 


## TODOS
- Support of ```object``` type.  Current version does not support OpenAPI ```object``` type (directly).  One will need to declare model classes and mark them with the @schema decorator and reference them.
- We are trying to lower the python version requirements.  Python2.7 support will require a significant recode because of how we generate the path spec data (we add a path_spec attribute to the instance method/handler which is allowed in Python3+ but not in Python 2.7).  There is a weird behavior in Python3.5 where in the parsing of the URL patterns returns an arbitrary pattern:  i.e. in some test runs, a URL pattern is detected as /test/{a}/{b} and sometimes it comes out as /test/{b}/{a}.  For now, only tests for Python 3.6 and Python 3.7 are passing (via tox).


## Comments

Please send your suggestions, comments to: r.duldulao@salarium.com

(c) 2018 [Salarium LTD](https://www.salarium.com).  All rights reserved. 

