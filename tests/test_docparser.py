#pylint: disable=all
from tornado_swirl.docparser import parse_from_docstring, PathSpec


def test_simple_parse_1():
    docstring = """This is the simple description"""

    path_spec = parse_from_docstring(docstring)
    assert isinstance(path_spec, PathSpec)
    assert path_spec.summary == "This is the simple description"


def test_simple_parse_2():
    docstring = """This is the simple description.

    Long description.
    """

    path_spec = parse_from_docstring(docstring)
    assert path_spec.summary == "This is the simple description.\n"
    assert path_spec.description == "Long description.\n"


def test_simple_parse_3():
    docstring = """This is the simple description.
    With a second line.

    Long description.
    With a second line.
    """

    path_spec = parse_from_docstring(docstring)
    assert path_spec.summary == "This is the simple description.\nWith a second line.\n"
    assert path_spec.description == "Long description.\nWith a second line.\n"


def test_simple_parse_4_with_path_params():
    docstring = """This is the simple description.
With a second line.

Long description.
With a second line.

Path Parameters:
    employee_uid (int) -- The employee ID.
"""

    path_spec = parse_from_docstring(docstring)
    assert path_spec.summary == "This is the simple description.\nWith a second line.\n"
    assert path_spec.description == "Long description.\nWith a second line.\n"

    pp = path_spec.path_params.get('employee_uid')
    assert pp.name == 'employee_uid'
    assert pp.type == 'int'
    assert pp.ptype == "path"
    assert pp.description == 'The employee ID.'
    assert pp.required == True


def test_simple_parse_5_with_query_params():
    docstring = """This is the simple description.
With a second line.

Long description.
With a second line.

Query Parameters:
    param1 (int) -- The param 1.
    param2 (Model) -- Required. The param 2.
"""

    path_spec = parse_from_docstring(docstring)
    assert path_spec.summary == "This is the simple description.\nWith a second line.\n"
    assert path_spec.description == "Long description.\nWith a second line.\n"

    qp = path_spec.query_params.get("param1")
    assert qp is not None
    assert qp.name == "param1"
    assert qp.type == "int"
    assert qp.ptype == "query"
    assert qp.required == False
    assert qp.description == "The param 1."

    qp2 = path_spec.query_params.get("param2")
    assert qp2 is not None
    assert qp2.name == "param2"
    assert qp2.type == "Model"
    assert qp2.required
    assert qp2.description == "The param 2."


def test_simple_parse_6_with_body_params():
    docstring = """This is the simple description.
With a second line.

Long description.
With a second line.

Query Parameters:
    param1 (int) -- The param 1.
    param2 (Model) -- Required. The param 2.

Request Body:
    test (Model) -- Required.  This is the bomb.
"""

    path_spec = parse_from_docstring(docstring)
    assert path_spec.summary == "This is the simple description.\nWith a second line.\n"
    assert path_spec.description == "Long description.\nWith a second line.\n"

    qp = path_spec.query_params.get("param1")
    assert qp is not None
    assert qp.name == "param1"
    assert qp.type == "int"
    assert qp.ptype == "query"
    assert qp.required == False
    assert qp.description == "The param 1."

    qp2 = path_spec.query_params.get("param2")
    assert qp2 is not None
    assert qp2.name == "param2"
    assert qp2.type == "Model"
    assert qp2.required
    assert qp2.description == "The param 2."

    body_params = path_spec.body_params
    assert body_params is not None
    


def test_simple_parse_6_with_body_params_and_headers():
    docstring = """This is the simple description.
With a second line.

Long description.
With a second line.

Headers:
    Authorization -- Required. the login.

Query Parameters:
    param1 (int) -- The param 1.
    param2 (Model) -- Required. The param 2.

Request Body:
    test (Model) -- Required.  This is the bomb.
"""

    path_spec = parse_from_docstring(docstring)
    assert path_spec.summary == "This is the simple description.\nWith a second line.\n"
    assert path_spec.description == "Long description.\nWith a second line.\n"

    qp = path_spec.query_params.get("param1")
    assert qp is not None
    assert qp.name == "param1"
    assert qp.type == "int"
    assert qp.ptype == "query"
    assert qp.required == False
    assert qp.description == "The param 1."

    qp2 = path_spec.query_params.get("param2")
    assert qp2 is not None
    assert qp2.name == "param2"
    assert qp2.type == "Model"
    assert qp2.required
    assert qp2.description == "The param 2."

    body_params = path_spec.body_params
    assert body_params is not None
  
    hp = path_spec.header_params.get("Authorization")
    assert hp is not None
    assert hp.name == "Authorization"
    assert hp.type == "string"
    assert hp.required


def test_simple_parse_6_with_body_params_and_headers_array_of_ints():
    docstring = """This is the simple description.
With a second line.

Long description.
With a second line.

Headers:
    Authorization -- Required. the login.

Query Parameters:
    param1 ([int]) -- The param 1.
    param2 (Model) -- Required. The param 2.

Request Body:
    test (Model) -- Required.  This is the bomb.
"""

    path_spec = parse_from_docstring(docstring)

    qp = path_spec.query_params.get("param1")
    assert qp is not None
    assert qp.name == "param1"
    assert qp.type == "array"
    assert qp.ptype == "query"
    assert qp.itype == "int"
    assert qp.required == False
    assert qp.description == "The param 1."

    qp2 = path_spec.query_params.get("param2")
    assert qp2 is not None
    assert qp2.name == "param2"
    assert qp2.type == "Model"
    assert qp2.required
    assert qp2.description == "The param 2."

    body_params = path_spec.body_params
    assert body_params is not None
    

    hp = path_spec.header_params.get("Authorization")
    assert hp is not None
    assert hp.name == "Authorization"
    assert hp.type == "string"
    assert hp.required


def test_cookie_section():
    docstring = """Cookie Monster

    Cookie:
        x (string) -- required.  Cookie monster raaa
    """
    path_spec = parse_from_docstring(docstring)

    assert path_spec.cookie_params
    cookie = path_spec.cookie_params.get("x")
    assert cookie is not None
    assert cookie.name == 'x'
    assert cookie.type == 'string'
    assert cookie.required
    assert cookie.description == 'Cookie monster raaa'


def test_response_200():
    docstring = """Response 200

    Response:
        x (Model) -- Response 200
    """
    path_spec = parse_from_docstring(docstring)

    assert path_spec.responses
    response = path_spec.responses.get("200")  # response ids are the http code
    assert response
    assert response.description == "Response 200"


def test_response_200_alternate_format():
    docstring = """Response 200

    200 Response:
        x (Model) -- Response 200
    """
    path_spec = parse_from_docstring(docstring)

    assert path_spec.responses
    response = path_spec.responses.get("200")  # response ids are the http code
    print(path_spec.responses)
    assert response
    assert response.description == "Response 200"


def test_response_201():
    docstring = """Response 200

    201 Response:
        None  -- ACCEPTED
    """
    path_spec = parse_from_docstring(docstring)

    assert path_spec.responses
    response = path_spec.responses.get("201")  # response ids are the http code
    print(path_spec.responses)
    assert response
    assert response.description == "ACCEPTED"


def test_error_responses():
    docstring = """Response 200

    Error Responses:
        400 -- {Not A Good Request}
        500 -- Hello
    """
    path_spec = parse_from_docstring(docstring)

    assert path_spec.responses
    response = path_spec.responses.get("400")  # response ids are the http code
    assert response
    assert response.description == "{Not A Good Request}"
    response = path_spec.responses.get("500")  # response ids are the http code
    assert response
    assert response.description == "Hello"


def test_docstring_test():
    docstring = """Test get

        Hiho

        Cookie:
            x (string) -- some foo

        Path Params:
            emp_uid (int) -- test
            date (date) -- test

        200 Response:
            test (string) -- Test data
        
        Error Response:
            400  -- Fudge
        """
    path_spec = parse_from_docstring(docstring)
    assert path_spec.summary == "Test get\n"
    assert path_spec.description == "Hiho\n"
    assert path_spec.cookie_params
    assert path_spec.cookie_params.get('x')
    assert path_spec.path_params
    assert path_spec.path_params.get("emp_uid")
    assert path_spec.responses
    assert path_spec.responses.get('200')
    assert path_spec.responses.get('400')

def test_schema_properties():
    docstring = """Test schema

    This is something

    Properties:
        name (string) -- required.  The name.
        age (int) -- The age.

    """
    path_spec = parse_from_docstring(docstring)
    assert path_spec.properties

    assert path_spec.properties.get('name')


def test_param_props():
    docstring = """Test schema

    This is something

    Properties:
        name (string) -- required.  The name.
        age (int) -- The age.
            minimum: 1
            maximum: 200


    """
    path_spec = parse_from_docstring(docstring)
    assert path_spec.properties

    assert path_spec.properties.get('name')
    assert path_spec.properties.get('age')
    assert path_spec.properties.get('age').description.strip() == 'The age.'
    assert path_spec.properties.get('age').kwargs.get('minimum') == 1