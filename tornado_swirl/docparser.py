import re
#objects
QUERYSPEC_REGEX = r"^(?P<name>\w+( +\w+)*)(\s+\((?P<type>[\w\[\]]+)\)?)?\s*(--(\s+((?P<required>required|optional)\.)?(?P<description>.*)?)?)?"

class PathSpec(object):

    def __init__(self):
        self.summary = ""
        self.description = ""
        self.path_params_section = "" #this will need to be parsed 
        self.query_params_section = ""
        self.header_section = ""
        self.formData_section = ""
        self.openapi_section = ""
        self.body_section = ""
        self.cookie_section = ""
        self.query_params = {}
        self.path_params = {}
        self.body_param = None  #there should only be one.
        self.header_params = {} 
        self.form_params = {}
        self.cookie_params = {}
    
    def _parse_cookie_param_section(self):
        if not self.cookie_section: 
            return
        lines = self.cookie_section.splitlines()
        cleaned_lines = self._clean_lines(lines)

        for line in cleaned_lines:
            matcher = re.match(QUERYSPEC_REGEX, line, re.IGNORECASE)
            param = Param(name=matcher.group('name'),
                dtype=matcher.group('type') or 'string',
                ptype="cookie",
                required=str(matcher.group('required')).lower() == "required",
                description=str(matcher.group('description')).strip()
            )
            self.cookie_params[param.name] = param


        
    def _parse_header_param_section(self):
        if not self.header_section:
            return

        #first merge lines without -- to previous lines
        lines = self.header_section.splitlines()
        cleaned_lines = self._clean_lines(lines)

        #parse the lines
        for line in cleaned_lines:
            matcher = re.match(QUERYSPEC_REGEX, line, re.IGNORECASE)
            param = Param(name=matcher.group('name'),
                dtype=matcher.group('type') or 'string',
                ptype="header",
                required=str(matcher.group('required')).lower() == "required",
                description=str(matcher.group('description')).strip()
            )
            self.header_params[param.name] = param


    def _parse_body_param_section(self):
        if not self.body_section:
            return

        
        #first merge lines without -- to previous lines
        lines = self.body_section.splitlines()
        cleaned_lines = self._clean_lines(lines)
        if cleaned_lines:
            line = cleaned_lines[0] #get the first one only 
            matcher = re.match(QUERYSPEC_REGEX, line, re.IGNORECASE)
            param = Param(name=matcher.group('name'),
                dtype=matcher.group('type') or 'string',
                ptype="body",
                required=not (str(matcher.group('required')).lower() == "optional"),
                description=str(matcher.group('description')).strip()
            )
            self.body_param = param
       

        
    def _parse_query_params_section(self):
        print(self.query_params_section)
        if not self.query_params_section:
            return

        #first merge lines without -- to previous lines
        lines = self.query_params_section.splitlines()
        cleaned_lines = self._clean_lines(lines)

        #parse the lines
        for line in cleaned_lines:
            matcher = re.match(QUERYSPEC_REGEX, line, re.IGNORECASE)
            param = Param(name=matcher.group('name'),
                dtype=matcher.group('type') or 'string',
                ptype="query",
                required=str(matcher.group('required')).lower() == "required",
                description=str(matcher.group('description')).strip()
            )
            self.query_params[param.name] = param

    def _parse_path_params_section(self):
        if not self.path_params_section:
            return

        lines = self.path_params_section.splitlines()
        cleaned_lines = self._clean_lines(lines)
        for i, line in enumerate(cleaned_lines, start=1):
            matcher = re.match(QUERYSPEC_REGEX, line, re.IGNORECASE)
            param = Param(name=matcher.group('name'),
                dtype=matcher.group('type') or 'string',
                ptype="path",
                description=str(matcher.group('description')).strip(),
                required=not (str(matcher.group('required')).lower() == "optional"),
                order=i
            )
            self.path_params[param.name] = param

    def _clean_lines(self, lines: []):
        cleaned_lines, lines = [ lines[0].strip() ], lines[1:]
        while lines:
            cur_line, lines = lines[0], lines[1:]
            if cur_line.lstrip().index('--') > 0:
                cleaned_lines.append(cur_line.strip())
            else:
                cleaned_lines[-1] = cleaned_lines[-1] + " " + cur_line.strip()
        return cleaned_lines

    
    def _clean_buffers(self):
        self.body_section = ""
        self.cookie_section = ""
        self.formData_section = ""
        self.path_params_section = ""
        self.query_params_section = ""
        



class Param(object):
    def __init__(self, name, dtype='string', ptype='path', required=False, description=None, order=0):
        self.name = name
        self.type = dtype
        self.ptype = ptype
        self.required = required
        self.description = description
        self.order = order
        self.itype = None
        if self.type.strip().startswith('[') and self.type.strip().endswith(']'):
            self.itype = self.type.strip()[1:-1]
            self.type = "array"
    
    def is_model_type(self):
        #TODO: connect with models lookup
        return False



S_START = 0
S_SUMMARY = 1
S_DESCRIPTION = 2
S_END = 3
S_BLANK = 4
S_PATH_PARAMS = 5
S_QUERY_PARAMS = 6
S_REQUEST_BODY = 7
S_SUCCESS_RESPONSES = 8
S_ERROR_RESPONSES = 9
S_DEPRECATED = 10
S_HEADER = 11
S_COOKIE = 12

#transitions
def transition_blank(fsm_obj):
    pass

def transition_summary(fsm_obj):
    fsm_obj.path_spec.summary += fsm_obj.current_line.lstrip()
    

def transition_description(fsm_obj):
    if fsm_obj.path_spec.description and fsm_obj.current_line:
        fsm_obj.path_spec.description += fsm_obj.current_line.lstrip()
    else:
        fsm_obj.path_spec.description = fsm_obj.current_line.lstrip()

def transition_path_params(fsm_obj):
    fsm_obj.path_spec.path_params_section += fsm_obj.current_line
    
def transition_query_params(fsm_obj):
    fsm_obj.path_spec.query_params_section += fsm_obj.current_line

def transition_request_body(fsm_obj):
    fsm_obj.path_spec.body_section += fsm_obj.current_line

def transition_header(fsm_obj):
    fsm_obj.path_spec.header_section += fsm_obj.current_line

def transition_cookie(fsm_obj):
    fsm_obj.path_spec.cookie_section += fsm_obj.current_line
    
#transitions
T_BLANK = transition_blank
T_SUMMARY = transition_summary

#conditions
def is_generic_line(line):
    if is_path_params_line(line):
        return False
    if is_query_params_line(line):
        return False
    if is_request_body_line(line):
        return False
    if is_header_line(line):
        return False
    if is_cookie_line(line):
        return False
    return True if line.strip() else False
    

def is_blank_line(line):
    return not line.strip()

def is_path_params_line(line):
    return line.strip().lower() in ('path parameter:', 'path param:', 'path parameters:', 'path params:', 'url parameters:', 'url params:')

def is_query_params_line(line):
    return line.strip().lower() in ('query parameters:', 'query params:', 'query parameter:', 'query param:')

def is_request_body_line(line):
    return line.strip().lower() == 'request body:'

def is_header_line(line):
    return line.strip().lower() in ("headers:", "header:", "http headers:", "http header:")    

def is_cookie_line(line):
    return line.strip().lower() in ("cookies:", "cookie:")

FSM_MAP = (
    {'src': S_START,
     'dst': S_SUMMARY,
     'condition': is_generic_line,
     'callback': transition_summary},
    {'src': S_SUMMARY,
     'dst': S_SUMMARY,
     'condition': is_generic_line,
     'callback': transition_summary},
    {'src': S_SUMMARY,
     'dst': S_BLANK,
     'condition': is_blank_line,
     'callback': transition_blank},
    {'src': S_BLANK,
     'dst': S_DESCRIPTION,
     'condition': is_generic_line,
     'callback': transition_description},
    {'src': S_DESCRIPTION,
     'dst': S_DESCRIPTION,
     'condition': is_generic_line,
     'callback': transition_description},
    {'src': S_DESCRIPTION,
     'dst': S_BLANK,
     'condition': is_blank_line,
     'callback': transition_blank},
    {'src': S_BLANK,
     'dst': S_PATH_PARAMS,
     'condition': is_path_params_line,
     'callback': transition_blank,},
    {'src': S_PATH_PARAMS,
     'dst': S_PATH_PARAMS,
     'condition': is_generic_line,
     'callback': transition_path_params,},
    {'src': S_PATH_PARAMS,
     'dst': S_BLANK,
     'condition': is_blank_line,
     'callback': transition_blank,},
    {'src': S_BLANK,
     'dst': S_QUERY_PARAMS,
     'condition': is_query_params_line,
     'callback': transition_blank,},
    {'src': S_QUERY_PARAMS,
     'dst': S_QUERY_PARAMS,
     'condition': is_generic_line,
     'callback': transition_query_params,},
     {'src': S_QUERY_PARAMS,
     'dst': S_BLANK,
     'condition': is_blank_line,
     'callback': transition_blank,},
    {'src': S_PATH_PARAMS,
     'dst': S_BLANK,
     'condition': is_blank_line,
     'callback': transition_blank,},
    {'src': S_BLANK,
     'dst': S_REQUEST_BODY,
     'condition': is_request_body_line,
     'callback': transition_blank,  #change to skip later
    },
    {'src': S_REQUEST_BODY,
     'dst': S_REQUEST_BODY,
     'condition': is_generic_line,
     'callback': transition_request_body,
    },
    {'src': S_REQUEST_BODY,
     'dst': S_BLANK,
     'condition': is_blank_line,
     'callback': transition_blank,
    },
    {'src': S_BLANK,
     'dst': S_HEADER,
     'condition': is_header_line,
     'callback': transition_blank,
    },
    {'src': S_HEADER,
     'dst': S_HEADER,
     'condition': is_generic_line,
     'callback': transition_header,
    },
     {'src': S_HEADER,
     'dst': S_BLANK,
     'condition': is_blank_line,
     'callback': transition_blank,
    },
    {'src': S_BLANK,
     'dst': S_COOKIE,
     'condition': is_cookie_line,
     'callback': transition_blank,
    },
    {'src': S_COOKIE,
     'dst': S_COOKIE,
     'condition': is_generic_line,
     'callback': transition_cookie,
    },
     {'src': S_COOKIE,
     'dst': S_BLANK,
     'condition': is_blank_line,
     'callback': transition_blank,
    },


)




class Parse_FSM:

    def __init__(self, lines):
        self.input_lines = lines
        self.current_state = S_START
        self.current_line = None
        self.path_spec = PathSpec()

    def run(self):
        for c in self.input_lines:
            if not self.process_next(c):
                print("skip '{}' in {}".format(c, self.current_state))
        self.path_spec._parse_query_params_section()
        self.path_spec._parse_path_params_section()
        self.path_spec._parse_body_param_section()
        self.path_spec._parse_header_param_section()
        self.path_spec._parse_cookie_param_section()
        #TODO: 
        self.path_spec._clean_buffers()

    def process_next(self, line):
        self.current_line = line
        frozen_state = self.current_state
        for transition in FSM_MAP:
            if transition['src'] == frozen_state:
                if self.iterate_re_evaluators(line, transition):
                    return True
        return False

    def iterate_re_evaluators(self, line, transition):
        condition = transition['condition']
        if condition(line):
            self.update_state(
                transition['dst'], transition['callback'])
            return True
        return False

    def update_state(self, new_state, callback):
        self.current_state = new_state
        callback(self)


def parse_from_docstring(docstring: str) -> PathSpec:
    #preprocess lines
    lines = docstring.splitlines(keepends=True)

    p = Parse_FSM(lines)
    p.run()

    return p.path_spec