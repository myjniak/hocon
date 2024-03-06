import re
from typing import Union

from ._quoted_string import parse_triple_quoted_string, parse_quoted_string
from .constants import SIMPLE_VALUE_TYPE, ELEMENT_SEPARATORS, SECTION_CLOSURES, WHITE_CHARS, \
    UNQUOTED_STR_FORBIDDEN_CHARS, _FLOAT_CONSTANTS, NUMBER_RE


def parse_simple_value(data: str, idx: int = 0) -> tuple[SIMPLE_VALUE_TYPE, int]:
    values = []
    contains_quoted_string = False
    while True:
        char = data[idx]
        if data[idx:idx + 3] == "\"\"\"":
            contains_quoted_string = True
            string, idx = parse_triple_quoted_string(data, idx + 3)
            values.append(string)
        elif char == "\"":
            contains_quoted_string = True
            string, idx = parse_quoted_string(data, idx + 1)
            values.append(string)
        elif char in ELEMENT_SEPARATORS + SECTION_CLOSURES:
            joined_value = "".join(values)
            if len(values) == 1 and not contains_quoted_string:
                return _cast_string_value(joined_value), idx
            return joined_value, idx
        elif char in WHITE_CHARS:
            idx += 1
            values.append(char)
        else:
            string, idx = _parse_unquoted_string(data, idx)
            values.append(string)


def _parse_unquoted_string(data: str, idx: int) -> tuple[str, int]:
    unquoted_key_end = UNQUOTED_STR_FORBIDDEN_CHARS + WHITE_CHARS
    key = data[idx]
    while True:
        idx += 1
        char = data[idx]
        if char not in unquoted_key_end:
            key += char
        else:
            return key.strip(), idx


def _cast_string_value(string: str) -> SIMPLE_VALUE_TYPE:
    if string.startswith("true"):
        return True
    if string.startswith("false"):
        return False
    if string.startswith("null"):
        return None
    if string in _FLOAT_CONSTANTS.keys():
        return _FLOAT_CONSTANTS[string]
    match = re.match(NUMBER_RE, string)
    if match is not None and match.group() == string:
        return _cast_to_number(string)
    return string


def _cast_to_number(string: str) -> Union[float, int]:
    if string.lstrip("-").isdigit():
        return int(string)
    return float(string)
