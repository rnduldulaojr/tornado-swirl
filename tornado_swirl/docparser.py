import re
import tornado_swirl._processors as procs
from tornado_swirl._parser_model import PathSpec


_QUERY_HEADERS = 'query headers'
_PATH_HEADERS = 'path headers'
_BODY_HEADERS = 'body headers'
_COOKIE_HEADERS = 'cookies'
_HEADER_HEADERS = 'headers'
_ERROR_HEADERS = 'errors'
_RESPONSE_HEADERS = 'responses'

# Header regexes, buffer processor func
_HEADERS = {
    _QUERY_HEADERS: (r"query param(s|eter(s)?)?:", procs._process_query),
    _PATH_HEADERS: (r"(path|url) param(s|eter(s)?)?:", procs._process_path),
    _BODY_HEADERS: (r"(request\s*)? body:", procs._process_body),
    _COOKIE_HEADERS: (r"cookie(s|(\s*param(s|eter(s)?)?)?)?:", procs._process_cookie),
    _HEADER_HEADERS: (r"(http\s*)?header(s)?:", procs._process_header),
    _ERROR_HEADERS: (r"(error(s|\s*response(s)?)?|default(\s*response(s)?)):", procs._process_errors),
    _RESPONSE_HEADERS: (r"((http\s+)?((?P<code>\d+)\s+))?response:", procs._process_response),
}

_HEADERS_REGEX = { key: (re.compile("^"+val+"$", re.IGNORECASE), processor) for (key, (val, processor)) in _HEADERS.items()}
_ALL_HEADERS = '|'.join([ rs for (rs, _) in _HEADERS.values()])
_ALL_HEADERS_REGEX = re.compile("^("+_ALL_HEADERS+")$", re.IGNORECASE)
_SECTION_HEADER_REGEX = re.compile(r"^([\w ]+):$")



S_START = 0
S_SUMMARY = 1
S_DESCRIPTION = 2
S_END = 3
S_BLANK = 4
S_SECTION = 5

# transitions

def _get_header_type(section_header):
    #returns header type and some info
    print(section_header)
    for (name, (regex, _)) in _HEADERS_REGEX.items():
        matcher = regex.match(str(section_header))
        if matcher:
            if name == _RESPONSE_HEADERS:
                return (name, { "code": matcher.group('code') or '200' })
            return (name, None)
    return (None, None)


def transition_blank(fsm_obj):
    pass


def transition_buffer(fsm_obj):
    fsm_obj._buffer += fsm_obj.current_line.lstrip()


def transition_section(fsm_obj):
    fsm_obj._cur_header = fsm_obj.current_line.strip()


def transition_process_buffer(fsm_obj):
    print("Processing buffer")
    #get cur header type
    htype, params = _get_header_type(fsm_obj._cur_header)
    print("Header type: ", htype)
    _, processor = _HEADERS_REGEX.get(htype, (None, None))

    #process the buffer
    if not processor:
        return
    if params:
        processor(fsm_obj, **params)
    else:
        processor(fsm_obj)
    fsm_obj.cur_header = None
    fsm_obj._buffer = ''

def transition_process_buffer_new_section(fsm_obj):
    transition_process_buffer(fsm_obj)
    transition_section(fsm_obj)


def transition_summary(fsm_obj):
    fsm_obj.path_spec.summary = fsm_obj._buffer
    print("Got summary: ", fsm_obj.path_spec.summary)
    fsm_obj._buffer = ""


def transition_description(fsm_obj):
    fsm_obj.path_spec.description += fsm_obj._buffer
    fsm_obj._buffer = ""





# transitions
T_BLANK = transition_blank
T_SUMMARY = transition_summary

# conditions

def is_generic_line(line):
    line = line.strip()
    if _SECTION_HEADER_REGEX.match(line):
        return False
    if line == "":
        return False
    if is_end(line):
        return False

    print("Detected generic line")
    return True 

def is_end(line):
    return line.strip() == "--THE END--"

def is_blank_line(line):
    print("Detected blank" if line.strip == "" else "")
    return line.strip() == ""

def is_generic_line_or_blank(line):
    return is_generic_line(line) or is_blank_line(line)

def is_section_header(line):
    print("Detected section header " + line if _SECTION_HEADER_REGEX.match(line.strip()) else "" )
    return True if _SECTION_HEADER_REGEX.match(line.strip()) else False


FSM_MAP = (
    {'src': S_START, 'dst': S_SUMMARY, 'condition': is_generic_line,
        'callback': transition_buffer},
    {'src': S_SUMMARY, 'dst': S_SUMMARY,
        'condition': is_generic_line, 'callback': transition_buffer},
    {'src': S_SUMMARY, 'dst': S_BLANK,
        'condition': is_blank_line, 'callback': transition_summary},
    {'src': S_SUMMARY, 'dst': S_END,
        'condition': is_end, 'callback': transition_summary},
    
    {'src': S_BLANK, 'dst': S_DESCRIPTION, 'condition': is_generic_line,
        'callback': transition_buffer},
    {'src': S_DESCRIPTION, 'dst': S_DESCRIPTION,
        'condition': is_generic_line, 'callback': transition_buffer},
    {'src': S_DESCRIPTION, 'dst': S_BLANK,
        'condition': is_blank_line, 'callback': transition_description},
    {'src': S_START, 'dst': S_SECTION, 
        'condition': is_section_header, 'callback': transition_section},
    {'src': S_BLANK, 'dst': S_SECTION,
        'condition': is_section_header, 'callback': transition_section},
    {'src': S_SECTION, 'dst': S_SECTION,
        'condition': is_generic_line_or_blank, 'callback': transition_buffer},
    {'src': S_SECTION, 'dst': S_SECTION,
        'condition': is_section_header, 'callback': transition_process_buffer_new_section},
    {'src': S_SECTION, 'dst': S_END,
        'condition': is_end, 'callback': transition_process_buffer
    },
    {'src': S_START, 'dst': S_END, 'condition': is_end, 'callback': transition_process_buffer},
    {'src': S_BLANK, 'dst': S_END, 'condition': is_end, 'callback': transition_process_buffer},
    {'src': S_DESCRIPTION, 'dst': S_END, 'condition': is_end, 'callback': transition_process_buffer},
 

)


class Parse_FSM:

    def __init__(self, lines):
        self.input_lines = lines + ["--THE END--"]
        self.current_state = S_START
        self.current_line = None
        self.path_spec = PathSpec()
        self._buffer = ''
        self._cur_code = None
        self._cur_header = None

    def run(self):
        for c in self.input_lines:
            if not self.process_next(c):
                print("skip '{}' in {}".format(c, self.current_state))

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
            print("current ", self.current_state)
            self.update_state(
                transition['dst'], transition['callback'])
            return True
        return False

    def update_state(self, new_state, callback):
        self.current_state = new_state
        print("new state ", self.current_state)
        callback(self)


def parse_from_docstring(docstring: str) -> PathSpec:
    # preprocess lines
    lines = docstring.splitlines(keepends=True)
    p = Parse_FSM(lines)
    p.run()
    return p.path_spec
