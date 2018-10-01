"""Parser FSM models."""


class PathSpec(object):
    """Represents the path specification of an REST API endpoint."""

    def __init__(self):
        self.summary = ""
        self.description = ""
        self.query_params = {}
        self.path_params = {}
        self.body_param = None  # there should only be one.
        self.header_params = {}
        self.form_params = {}
        self.cookie_params = {}
        self.responses = {}
        self.properties = {}


class SchemaSpec(object):
    """Represents a REST API component schema."""

    def __init__(self):
        self.name = ""
        self.summary = ""
        self.description = ""
        self.properties = {}


class Param(object):
    """REST API section parameter"""

    def __init__(self, name, dtype='string', ptype='path',
                 required=False, description=None, order=0):
        self.name = name
        if dtype:
            self.type = dtype.strip()
        else:
            self.type = None
        self.ptype = ptype
        self.required = required
        self.description = description
        self.order = order
        self.itype = None
        self.kwargs = {}
        if self.type and self.type.startswith('[') and self.type.endswith(']'):
            self.itype = self.type[1:-1]
            self.type = "array"

        if self.type and self.type.startswith('enum[') and self.type.endswith(']'):
            content = [c.strip() for c in
                       self.type[self.type.find('[')+1:self.type.rfind(']')].split(',')]

            self.itype = {
                "enum": content
            }
            self.type = "string"
