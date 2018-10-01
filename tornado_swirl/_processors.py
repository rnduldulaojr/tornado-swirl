import re

from ._parser_model import Param
import numbers

from .settings import get_schemas
# objects
QUERYSPEC_REGEX = r"^(?P<name>\w+( +\w+)*)(\s+\((?P<type>[\w, :/\[\]]+)\)?)?\s*(--(\s+((?P<required>required|optional)\.)?(?P<description>.*)?)?)?$"
PARAM_MATCHER = re.compile(QUERYSPEC_REGEX, re.IGNORECASE)
RESPONSE_REGEX = r"^((http\s+)?((?P<code>\d+)\s+))?response:$"
RESPONSE_MATCHER = re.compile(RESPONSE_REGEX, re.IGNORECASE)
ERRORSPEC_REGEX = r"^(?P<code>\d+)\s*--\s*(?P<description>.*)$"
ERRORSPEC_MATCHER = re.compile(ERRORSPEC_REGEX, re.IGNORECASE)

# _PROP_SPEC_REGEX = re.compile("(?P<name>\w+): (?P<value>\w[\w\s]*)")}


class number(numbers.Number):
    def __new__(cls, val):
        if str(val).find('.'):
            try:
                return float(val)
            except ValueError:
                return val
        try:
            return int(val)
        except ValueError:
            return val


class boolean(object):
    def __new__(cls, val):
        return val in ('True', 'true', '1', True)


_PROPS_TYPE_LOOKUP = {
    boolean: ('exclusiveMinimum', 'exclusiveMaximum', 'uniqueItems'),
    number: ('minimum', 'maximum', 'multipleOf', 'minItems', 'maxItems')
}


def _lookup_type_of(name):
    for t, names in _PROPS_TYPE_LOOKUP.items():
        if name in names:
            return t
    return str


def _process_params(fsm_obj, ptype, required_func=None):
    # get buffer and conver
    # first merge lines without -- to previous lines
    if required_func is None:
        required_func = lambda x, y: x == y

    lines = fsm_obj._buffer.splitlines()
    cleaned_lines = _clean_lines(lines)
    params = {}
    # parse the lines
    for i, line in enumerate(cleaned_lines):
        matcher = PARAM_MATCHER.match(line.lstrip())
        if not matcher:
            continue
        param = Param(name=matcher.group('name'),
                      dtype=matcher.group('type'),
                      ptype=ptype,
                      required=required_func(str(matcher.group('required')
                                                 ).lower(), "required"),
                      order=i,
                      )
        description = str(matcher.group('description')).strip()
        desc, kwargs = _get_description_props(description)
        param.description = desc.strip()
        param.kwargs = kwargs
        params[param.name] = param
    return params


def _process_path(fsm_obj, **kwargs):
    fsm_obj.spec.path_params = _process_params(
        fsm_obj, "path", lambda x, y: True)
    _set_default_type(fsm_obj.spec.path_params, "string")
    fsm_obj._buffer = ""


def _get_real_value(name, value):
    dtype = _lookup_type_of(name)

    return dtype(value)


def _get_description_props(description: str):
    """Returns description, kwargs"""
    kwargs = {}

    index = description.rfind(':')
    while index > -1:
        description, value = description[0:index], description[index+1:]
        boundary = max(description.rfind(' '), description.rfind('\n'))
        description, name = description[0:boundary], description[boundary+1:]
        kwargs[name] = _get_real_value(name, value.strip())
        index = description.rfind(':')

    return description, kwargs

def _set_default_type(dval, dtype):
    for (name, param) in dval.items():
        if not param.type:
            dval[name].type = dtype
    

def _process_query(fsm_obj, **kwargs):
    fsm_obj.spec.query_params = _process_params(fsm_obj, "query")
    _set_default_type(fsm_obj.spec.query_params, "string")
    fsm_obj._buffer = ""



def _process_body(fsm_obj, **kwargs):
    # first merge lines without -- to previous lines
    # TODO: change this
    fsm_obj.spec.body_params = _process_params(fsm_obj, "body", lambda x, y: True)
    #check the params and guess the content type
    _set_default_type(fsm_obj.spec.body_params, "string")
    fsm_obj._buffer = ''

def _process_cookie(fsm_obj, **kwargs):
    fsm_obj.spec.cookie_params = _process_params(fsm_obj, "cookie")
    _set_default_type(fsm_obj.spec.cookie_params, "string")
    fsm_obj._buffer = ""


def _process_header(fsm_obj, **kwargs):
    fsm_obj.spec.header_params = _process_params(fsm_obj, "header")
    #convert all types to string if None
    _set_default_type(fsm_obj.spec.header_params, "string")
    fsm_obj._buffer = ""


def _process_response(fsm_obj, **kwargs):
    lines = fsm_obj._buffer.splitlines()
    cleaned_lines = _clean_lines(lines)
    cur_code = kwargs.get('code', '200')
    print("Cur_code: ", cur_code)
    res = _process_params(fsm_obj, "response")
    if res:
        item = list(res.values())[0]
        item.name = cur_code
        fsm_obj.spec.responses.update({
            cur_code: item
        })
    fsm_obj._buffer = ""


def _process_properties(fsm_obj, **kwargs):
    fsm_obj.spec.properties = _process_params(fsm_obj, "property")
    _set_default_type(fsm_obj.spec.properties, "string")
    fsm_obj._buffer = ""


def _process_errors(fsm_obj, **kwargs):
    fsm_obj.spec.responses.update(_process_params(fsm_obj, "response"))
    fsm_obj._buffer = ""


def _clean_lines(lines: []):
    cleaned_lines, lines = [lines[0].strip()], lines[1:]
    while lines:
        cur_line, lines = lines[0], lines[1:]
        try:
            cur_line.lstrip().index(' -- ')
            cleaned_lines.append(cur_line.strip())
        except ValueError:
            cleaned_lines[-1] = cleaned_lines[-1] + " " + cur_line.strip()
    return cleaned_lines
