class PathSpec(object):
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
    def __init__(self):
        self.name = ""
        self.summary = ""
        self.description = ""
        self.properties = {}

class Param(object):
    def __init__(self, name, dtype='string', ptype='path', required=False, description=None, order=0):
        self.name = name
        self.type = dtype
        self.ptype = ptype
        self.required = required
        self.description = description
        self.order = order
        self.itype = None
        if self.type and self.type.strip().startswith('[') and self.type.strip().endswith(']'):
            self.itype = self.type.strip()[1:-1]
            self.type = "array"

    def is_model_type(self):
        # TODO: connect with models lookup
        return False