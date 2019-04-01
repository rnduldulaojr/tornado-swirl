# Tornado-Swirl Tutorial

## Initializing Your API

Describe your REST API before initializing your app:

```python
import tornado_swirl as swirl

swirl.describe(title="My REST API", description="Example API that does wonders")

```

Describe your REST API with enabled methods:

```python
import tornado_swirl as swirl

swirl.describe(title="My REST API", description="Example API that does wonders",
               enabled_methods=['get', 'post'])

```


Custom headers on the Swagger UI handlers and Spec:
```python
import tornado_swirl as swirl

swirl.describe(title="My REST API", description="Example API that does wonders",
               swagger_ui_handlers_header=[
                   ('Cache-Control', 'public'),
                   ('Cache-Control', 'max-age=300')
               ],
               swagger_spec_headers=[
                   ('Cache-Control', 'no-cache')
               ],)

```

Adding Security Schemes:
```python
from tornado_swirl as swirl
from tornado_swirl.openapi import security

swirl.describe(title="My REST API", description="Example API that does wonders")

#setup security scheme
scheme1 = security.APIKey('X-CUSTOM-KEY', location="header")
scheme2 = security.HTTP('bearer', bearerFormat='JWT')

swirl.add_security_scheme('my_custom_key', scheme1)
swirl.add_security_scheme('my_http_key' , scheme2)


```


## Setting up Documenting Your Handlers and Models

Swirl derives OpenAPI 3.0 paths and components from your docstrings.  At the moment Swirl only parses Google-style (like) formatted docstrings.

REST API Handlers will need to be decorated with the ```@restapi```decorator with the path of the API as parameter.

REST API Models/components should be decorated with the swirl ```@schema``` decorator.

For example:

```python
import tornado_swirl as swirl

swirl.describe(title='Test API', description='Just things to test')
swirl.add_global_tag(name='MyTag', description='my tag description', url='http://foo.com/tags')

@swirl.restapi('/path/to/api')
class MyHandler(tornado.web.RequestHandler):
    async def get():
        """This will be the API path summary.

        While the long description will be the API description.

        Query Parameters:
            date (date) -- Required.  The target date.
            sort (enum[asc, desc]) -- Optional.  Sort order. 
            items (int) -- Optional.  Number of items to display.
                minimum: 100    maximum: 200
        
        200 Response:
            items ([string]) -- List of random strings.
        
        Error Responses:
            400 (ErrorResponse) -- Bad Request.
            500 (ErrorResponse) -- Internal Server Error.

        Tags:
            MyTag
        """
        self.finish()

@swirl.schema
class ErrorResponse(object):
    """Error response object.

    Properties:
        code (int) -- Required.  Error code.
        message (string) -- Error description.
    """
    pass

def make_app():
    return Application(swirl.api_routes(), autoreload=True)

if __name__ == "__main__":
    app = make_app()
    app.debug = True
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
```

Run the app

```sh
% python app.py
```

Then view the API spec by pointing your browser to ```http://localhost:8888/swagger/spec``` to view the JSON spec:

```json
{
    "openapi": "3.0.0",
    "info": {
        "title": "Test API",
        "description": "Just things to test",
        "version": "v1.0"
    },
    "servers": [
        {
            "url": "http://localhost:8888/",
            "description": "This server"
        }
    ],
    "schemes": [
        "http"
    ],
    "paths": {
        "/path/to/api": {
            "get": {
                "operationId": "MyHandler.get",
                "summary": "This will be the API path summary.",
                "description": "While the long description will be the API description.",
                "parameters": [
                    {
                        "in": "query",
                        "name": "date",
                        "required": true,
                        "description": "The target date.",
                        "schema": {
                            "type": "string",
                            "format": "date"
                        }
                    },
                    {
                        "in": "query",
                        "name": "sort",
                        "required": false,
                        "description": "Sort order.",
                        "schema": {
                            "type": "string",
                            "enum": [
                                "asc",
                                "desc"
                            ]
                        }
                    },
                    {
                        "in": "query",
                        "name": "items",
                        "required": false,
                        "description": "Number of items to display.",
                        "schema": {
                            "type": "integer"
                        }
                    }
                ],
                "responses": {
                    "200": {
                        "description": "List of random strings.",

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
                    },
                    "400": {
                        "description": "Bad Request.",
                        "content": null
                    },
                    "500": {
                        "description": "Internal Server Error.",
                        "content": null
                    }
                }
                "tags": [
                    "MyTag"
                ]
            }
        }
    },
    "tags": [
        { 
            "name": "MyTag",
            "description": "my tag description",
            "externalDocs": {
                "url": "http://foo.com/tags"
            }
        }
    ],
    "components": {
        "schemas": {
            "ErrorResponse": {
                "type": "object",
                "required": [
                    "code"
                ],
                "properties": {
                    "code": {
                        "type": "integer"
                    },
                    "message": {
                        "type": "string"
                    }
                }
            }
        }
    }
}

```

Alternatively you can also view your API spec via the built in Swagger UI:  ```http://localhost:8888/swagger/spec.html```


## Docstring Format

The OpenAPI 3.0 spec is generated from your Handler method docstrings and model class docstrings.  They follow the following format:

```python
"""[Summary]

[Long Description]

[Section Header:]
    Var1 (Type) -- (Required.|Optional.) Param/var description
    Var2 (Type) -- Var 2 description.
        schemaprop1: value1    schemaprop2: value2
        schemaprop3: value3
...
"""
```

The summary and the long decriptions describe the path or model element.

The section headers have definite possible values that are case insensitive.  For example, to describe HTTP Headers, the section header can be ```HTTP Headers:``` or ```Request Headers:``` in any case combination.  Each section describes a set of parameter types and/or properties.  


| Parameter/Variable Type | Possible Section Header Value Pattern | Example |
| ----------------------- | ------------------------------------- | --------|
| HTTP Request Headers    | ^(http\s+)?(request\s+)?header(s)?:$ | ```HTTP Header:```, ```Request Headers:```, ```Headers:``` |
| URL/Path Parameters | ^(path\|url) param(s\|eter(s)?)?:$ | ```Path params:```, ```URL Parameters:``` |
| Query Parameters | ^query param(s\|eter(s)?)?:$ | ```Query Params:```, ```Query Parameter:``` |
| Cookies | ^cookie(s\|(\s*param(s\|eter(s)?)?)?)?:$ | ```Cookies:```, ```Cookie Params:``` |
| Request Body | ^(request\s+)?body:$ | ```Body:```, ```Request Body:``` |
| HTTP Response | ^((http\s+)?((?P<code>\d+)\s+))?response:$ | ```HTTP 200 Response:```, ```201 Response:```,  ```Response:``` (Default 200) |
| HTTP Error Response | ^(error(s\|\s\*response(s)?)?\|default(\s\*response(s)?)):$ | ```Errors:```, ```Error Responses:```, ```Default:``` |
| Model Properties | ^(propert(y\|ies):)$ | ```Properties:``` or ```Property:``` |
| Security | ^(security:) | ```Security:``` |
| Tags | ^tags:$ | ```Tags:``` |

TODO: HTTP Response Headers.

For example:

```python
"""Example with Query params.

Query Parameters:
    id (int) -- Required. The ID.
    age (int) -- The age.
        minimum: 1    maximum: 300
"""
```

## Describing Variables/Parameters

The variables or properties described in each section is laid out in the same format:

```
var_name (type) -- (Required.|Optional.) Description
    schemaprop1: value1      schemaprop2: value2
```

Only the ```var_name``` and the double dash (--) separator is required.  For the case of HTTP Response sections, the ```var_name``` should be the HTTP code.  For example:

```python
"""Foo bar

Errors:
    400 -- Bad Request
    500 (ErrorResponse) -- Internal server error described by a model.
"""
```

Putting a ```Required.``` or ```Optional.``` marker before the variable description will mark the variable as required or optional.  This has no effect on sections where all variables are required, for example, Path Parameters are always required.   


## Simple Variable Types

The following are the values that can be used as types:

* Integer types:  ```integer```, ```int```, ```long```, ```int32```, ```int64```.  The variable will be marked as an ```integer```.  If ```int32``` or ```int64``` is specified, then the variable will be an ```integer``` with format as either ```int32``` or ```int64```.  ```long``` is just an alias for ```int64```.  For example:  ```{"type": "integer", "format": "int32"}```.
* Number types: ```number```, ```float```, ```double```.  Variable will be of ```type: number```.  If ```float``` or ```double``` is specified, then those values will be the format value, e.g. ```{"type": "number", "format": "float"}```.
* String types: ```string```, ```str```.  Variable schema will appear as ```{"type": "string"}```.
* More string types (via format): ```date```, ```date-time```, ```password```, ```byte```, ```binary```, ```email```, ```uuid```, ```uri```, ```hostname```, ```ipv4```, ```ipv6```,  These are all ```string``` formats.  The resulting schema for the variable would be for example: ```{"type": "string", "format": "date-time"}```
* Boolean Type:  ```boolean``` or ```bool```
* File Type:  ```file```.  File type schema will come out as ```{"type": "string", "format": "binary"}```.  TODO:  alternative file formats
* Object Type: ```object```.  Free form object.

## Simple Variable Types with Explicit Format and File Types

Types can be declared as
```
type:format
```

For example:
```python
"""
Query Params:
    id (integer:int32) -- Some int example

Request Body:
    inputFile (file:image/jpeg) -- File type example
"""
```
## Array/List Types

To specify a list/array type, enclose the item types with square brackets.  For example:

```python
"""Example list param

Request Body:
    ids [int] -- List of ints.
"""
```

The resulting schema for ids should be:
```json
"ids": {
    "schema": {
        "type": "array",
        "items": {
            "type": "integer"
        }
    }
}
```

Another example for good measure:
```python
"""Example list of PNG files!

Request Body:
    files [file:image/png] -- Uploading a lot of files.
"""
```

## Enum Types

Example:
```python
"""
Query Params:
    sort (enum[asc, desc]) -- Optional.  Sort order.

"""
```

Will be converted to spec as:
```json
"sort": {
    "schema": {
        "type": "string",
        "enum": ["asc", "desc"]
    }
}
```

## Components/Schema/Model Types

Any type identifier that is not mentioned in this document will be considered as an REST API schema.  As such, Swirl will make a reference object (```$ref```) as the schema.

Example:
```python
"""
Request Body:
    user (User) -- User data.
"""
```
```User``` will be detected as a user-defined type.  The schema value for it will come back as:

```json
{"user": {
    "schema": {
        "$ref": "#/components/schemas/User"
        }
    }
}
```

## ```object``` Type

Free form objects.

```
"""
Request Body:
    data (object) -- Free form object.
"""
```



## Combination Types:  ```anyOf```, ```allOf```, ```oneOf```, ```not```

Use:
* ```anyOf[ <comma delimited list of model names>]```
* ```allOf[ ... ]```
* ```oneOf[ ... ]```
* ```not[ ... ]```

Example:
```
"""
Request Body:
    data (anyOf[A, B, C])
"""
```

Resulting Spec:
```json
{ "data" : {
    "schema": {
        "anyOf": [
            {"$ref": "#/components/schemas/A"},
            {"$ref": "#/components/schemas/B"},
            {"$ref": "#/components/schemas/C"},
        ]
    }
  }
}
```

## Schema Inheritance

Swirl will now go up the inheritance tree (MRO) to get references to the current schema's superclasses (except object).

```python
@schema
class User(object):
    """User object
    
    Properties:
        name (string) -- Required.  User name.
    """

@schema
class Admin(User):
    """Admin User

    Properties:
       superpowers ([string]) -- List of superpowers.
    """
```

-- will produce:

```json
"components":{  
   "schemas":{  
      "User":{  
         "type":"object",
         "description":"User object",
         "required":[  
            "name"
         ],
         "properties":{  
            "name":{  
               "type":"string",
               "description":"The name"
            }
         }
      },
      "Admin":{  
         "allOf":[  
            {  
               "$ref":"#/components/schemas/User"
            },
            {  
               "type":"object",
               "description":"Admin User",
               "properties":{  
                  "superpowers":{  
                     "type":"array",
                     "items":{  
                        "type":"string"
                     },
                     "description":"list of superpowers"
                  }
               }
            }
         ]
      
```

## Documenting Responses

The following can be used as section headers for HTTP 200 Ok responses:

* ```200 Response:```
* ```Return:``` or ```Returns:```
* ```HTTP Response:``` or just ```Response:```

For non-200 responses, you can use the following examples:

* ```HTTP 201 Response:``` or without the acronym, i.e. ```201 Response:```

To have a clear separation, we've decided to use a different section header for error messages.

* ```Errors:``` or ```Error Responses:```
* ```Default:```

The error responses is described by their error code (HTTP Error code).

Example:
```
"""
Returns:
    data (User) -- Successful operation (HTTP 200 Ok)

201 Response:
    response (None) -- Accepted status.

Errors:
    400 -- Bad Request
    401 -- Unauthorized

"""
```

## Tags

You can define a global tag using the `add_global_tag` function:

```python
swagger.add_global_tag(name='yourtag', description='desc', url='http://foo.com/tags')
```

`description` and `url` parameters are optional.

To apply a tag to your handler method, add a `Tags:` or `Tag:` section where the tags are defined one tag per line.

```python
"""With tag!

Tag:
    mytag
"""
```

## Security

You can set the security scheme of the API endpoint by adding a ```Security:``` section.  The items should 
be described with the name registered with ```add_security_scheme(name, scheme)``` call.  If an unregistered
name is used, it will be ignored in the generated swagger spec.

```python
"""With security scheme!

Security:
    my_custom_key
"""
```

If more than one security scheme is specified, (for now) follow the standard parameter description 
and use ```--``` for each scheme.

```python
"""With security scheme!

Security:
    my_custom_key --
    my_http_key --
"""
```



## Documenting Schemas

To mark a class as a component schema, just use the Swirl @schema decorator.

```python
@schema
class SomeUserClass(object):
    """My User class

    Properties:
        name (string) -- Required.  Name of user.
        id (int) -- Required.  ID of user.
    
    """
```

The docstring format should be the same as the REST API paths, although only ```Properties:``` or ```Property:``` section header is recognized here.


## Deprecated APIs/Schemas

To mark an API as deprecated, add ```Deprecated``` or ```[Deprecated]``` to your python docs in a line of its own.   It can be all caps.

```python
@swirl.restapi('/path/to/api')
class MyHandler(tornado.web.RequestHandler):
    async def get():
        """This will be the API path summary.

        DEPRECATED

        ...
        """
```

## Getting The Routes

You will need to use the swirl Tornado Application wrapper class and get the API routes registered via ```@restapi``` decorator using the ```api_routes()``` function.

```python
import tornado_swirl as swirl
. . .

def make_app():
    return swirl.Application(swirl.api_routes())

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()

```

...and then you're good to go.

## TODOS

## Comments

Please send your suggestions, comments to: r.duldulao@salarium.com

(c) 2018 [Salarium LTD](https://www.salarium.com).  All rights reserved. 



















