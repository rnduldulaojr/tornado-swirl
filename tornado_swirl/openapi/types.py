
class SchemaMixin(object):

    @property
    def schema(self):
        schema = {"type": self.name}
        if self.format:
            schema.update({"format": self.format})
        if self.kwargs:
            print(self.kwargs)
            schema.update(self.kwargs)  # TODO: check the validity
        return schema


class Type(object):
    """Represents an open api type"""

    def __new__(cls, val, *args, **kwargs):
        instance = Type._determine_type(str(val).strip(), **kwargs)
        return instance if instance else super(Type, cls).__new__(cls, *args, **kwargs)

    def __init__(self, val, *args, **kwargs):
        pass

    @staticmethod
    def _determine_type(val: str, **kwargs):
        if val == "" or val is None:
            return NoneType()
        if val.startswith("[") and val.endswith("]"):
            return ArrayType(val[1:-1], **kwargs)
        if val.startswith("enum[") and val.endswith("]"):
            return EnumType(val[5:-1])
        if val.startswith("oneOf[") and val.endswith("]"):
            return CombineType("oneOf", val[6:-1])
        if val.startswith("anyOf[") and val.endswith("]"):
            return CombineType("anyOf", val[6:-1])
        if val.startswith("allOf[") and val.endswith("]"):
            return CombineType("allOf", val[6:-1])
        if val.startswith("not[") and val.endswith("]"):
            return CombineType("not", val[4:-1])

        # this must be builtin or a model
        return Type._get_builtin_type(val, **kwargs)

    @staticmethod
    def _get_builtin_type(val: str, **kwargs):
        dtype = val
        dformat = None
        colon = val.find(':')
        if colon > 1:
            dtype = val[:colon]
            dformat = val[colon+1:]

        # integer type
        if dtype in ("int", "integer", "int32"):
            return IntType(dtype, dformat, **kwargs)
        elif dtype == "file":
            return FileType(dformat, **kwargs)
        elif dtype in ("long", "int64"):
            return IntType(dtype, dformat, **kwargs)
        elif dtype in ("number", "float", "double"):
            return NumberType(dtype, dformat, **kwargs)
        elif dtype in ("string", "str", "date", "date-time", "password", "byte", "binary", "email",
                       "uuid", "uri", "hostname", "ipv4", "ipv6"):
            return StringType(dtype, dformat, **kwargs)
        elif dtype in ("bool", "boolean"):
            return BoolType()
        # TODO:  support for object type
        return ModelType(dtype)

    @property
    def schema(self):
        pass  # need to override at the subclass


class FileType(object):
    def __init__(self, contents, **kwargs):
        self.name = "file"
        self.contents = contents
        self.kwargs = kwargs

    @property
    def schema(self):
        return {"type": "string", "format": "binary"}


class ArrayType(object):
    def __init__(self, contents, **kwargs):
        self.name = "array"
        self.items_type = Type(contents)
        self.kwargs = kwargs

    @property
    def schema(self):
        return {"type": "array", "items": self.items_type.schema}


class CombineType(object):
    def __init__(self, name, contents, **kwargs):
        self.name = name
        self.vals = []
        vals = contents.strip().split(",")
        self.vals = [Type(val.strip()) for val in vals]
        self.kwargs = kwargs

    @property
    def schema(self):
        return {self.name: [x.schema for x in self.vals]}


class NoneType(object):
    def __init__(self, **kwargs):
        self.name = "None"
        self.kwargs = kwargs

    @property
    def schema(self):
        return None


class BoolType(SchemaMixin):
    def __init__(self, **kwargs):
        self.name = 'boolean'
        self.kwargs = kwargs
        self.format = None


# simple Types


class IntType(SchemaMixin):
    def __init__(self, name, format, **kwargs):
        self.name = "integer"
        self.format = None
        if name == "long":
            self.format = "int64"
        elif name in ("int32", "int64"):
            self.format = name
        elif format:
            self.format = format  # TODO: check format value
        self.kwargs = kwargs


class NumberType(SchemaMixin):
    def __init__(self, name, format, **kwargs):
        self.name = "number"
        self.format = None
        if name in ("float", "double"):
            self.format = name
        elif format:
            self.format = format
        self.kwargs = kwargs


class StringType(SchemaMixin):
    def __init__(self, name, format, **kwargs):
        self.name = "string"
        self.format = None
        if name in ("date", "date-time", "password", "byte", "binary", "email",
                    "uuid", "uri", "hostname", "ipv4", "ipv6"):
            self.format = name
        elif format:
            self.format = format
        self.kwargs = kwargs


class EnumType(SchemaMixin):
    def __init__(self, values):
        self.name = "string"
        self.format = None
        vals = values.strip().split(",")
        vals = [val.strip() for val in vals]
        self.kwargs = {"enum": vals}


class ModelType(object):
    def __init__(self, name):
        self.name = name

    @property
    def schema(self):
        return {"$ref": "#/components/schemas/" + self.name}
