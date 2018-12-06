"""Parser FSM models."""


class PathSpec(object):
    """Represents the path specification of an REST API endpoint."""

    def __init__(self):
        self.summary = ""
        self.description = ""
        self.query_params = {}
        self.path_params = {}
        self.body_params = {}
        self.header_params = {}
        self.form_params = {}
        self.cookie_params = {}
        self.responses = {}
        self.properties = {}
        self.tags = {}
        self.deprecated = False


class SchemaSpec(object):
    """Represents a REST API component schema."""

    def __init__(self):
        self.name = ""
        self.summary = ""
        self.description = ""
        self.deprecated = False
        self.properties = {}


class Param(object):
    """REST API section parameter"""

    def __init__(self, name, dtype='string', ptype='path',
                 required=False, description=None, order=0):
        self.name = name
        self.type = dtype
        self.ptype = ptype
        self.required = required
        self.description = description
        self.order = order
        self.kwargs = {}
        