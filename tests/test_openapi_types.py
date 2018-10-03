"""OpenAPI types tests
"""
from tornado_swirl.openapi.types import Type

#simple types

def test_ints():
    """Test int type"""
    cases = [
        #name, inp value, kwargs, dict schema result
        ("Simple int1", "int",{},{"type":"integer"}),
        ("Simple int2", "integer", {}, {"type":"integer"}),
        ("Simple int3", "int32", {}, {"type":"integer", "format":"int32"}),
        ("Simple int4", "long", {}, {"type":"integer", "format":"int64"}),
        ("simple int5 with kwargs", "integer", {"minimum": 10}, {"type":"integer", "minimum": 10}),
        ("simple int5 with format kwargs", "integer:int32", {"minimum": 10}, {"type":"integer", "format":"int32", "minimum": 10}),

    ]

    for name, inp, kwargs, result  in cases:
        typ = Type(inp, **kwargs)
        assert typ.schema == result, name

def test_floats():
    """Test floats"""
    cases = [
        ("Simple float1", "number", {}, {"type":"number"}),
        ("Simple float2", "float", {}, {"type":"number", "format":"float"}),
        ("Simple float3", "double", {}, {"type":"number", "format":"double"}),
        ("Simple float4", "number:float", {"minimum": 1.0}, {"type":"number", "format":"float", "minimum":1.0}),
    ]
    for name, inp, kwargs, result  in cases:
        typ = Type(inp, **kwargs)
        assert typ.schema == result, name

def test_strings():
    """Test strings"""
    cases = [
        ("Test 1", "str", {}, {"type": "string"}),
        ("Test 2", "string", {}, {"type": "string"}),
        ("Test 3", "str:date", {}, {"type": "string", "format": "date"}),
        ("Test 4", "uuid", {}, {"type": "string", "format": "uuid"})
    ]
    for name, inp, kwargs, result  in cases:
        typ = Type(inp, **kwargs)
        assert typ.schema == result, name

def test_array():
    """Test array"""
    cases = [
        ("Test 1", "[integer]", {}, {"type":"array", "items": {"type":"integer"}})
    ]
    for name, inp, kwargs, result  in cases:
        typ = Type(inp, **kwargs)
    assert typ.schema == result, name


def test_enum():
    """Test array"""
    cases = [
        ("Test 1", "enum[a,b,c]", {}, {"type":"string", "enum": ["a", "b", "c"]})
    ]
    for name, inp, kwargs, result  in cases:
        typ = Type(inp, **kwargs)
    assert typ.schema == result, name


def test_combine_types():
    cases = [
        ("Test 1", "anyOf[A,B,C]", {}, {"anyOf": [{"$ref":"#/components/schemas/A"},{"$ref":"#/components/schemas/B"},{"$ref":"#/components/schemas/C"}]}),
        ("Test 2", "allOf[A,B,C]", {}, {"allOf": [{"$ref":"#/components/schemas/A"},{"$ref":"#/components/schemas/B"},{"$ref":"#/components/schemas/C"}]}),
        ("Test 3", "oneOf[A,B,C]", {}, {"oneOf": [{"$ref":"#/components/schemas/A"},{"$ref":"#/components/schemas/B"},{"$ref":"#/components/schemas/C"}]}),
    ]
    for name, inp, kwargs, result  in cases:
        typ = Type(inp, **kwargs)
    assert typ.schema == result, name


