import re
from json import JSONDecoder
from typing import Union

from ._quoted_string import parse_triple_quoted_string, parse_quoted_string
from .constants import SIMPLE_VALUE_TYPE, ELEMENT_SEPARATORS, SECTION_CLOSURES, WHITE_CHARS, \
    UNQUOTED_STR_FORBIDDEN_CHARS, _FLOAT_CONSTANTS, NUMBER_RE


def parse_simple_value(data: str, idx: int = 0) -> tuple[SIMPLE_VALUE_TYPE, int]:
    value = []
    while True:
        char = data[idx]
        if data[idx:idx + 3] == "\"\"\"":
            string, idx = parse_triple_quoted_string(data, idx + 3)
            value.append(string)
        elif char == "\"":
            string, idx = parse_quoted_string(data, idx + 1)
            value.append(string)
        elif char in ELEMENT_SEPARATORS + SECTION_CLOSURES:
            return _cast_string_value("".join(value)), idx
        elif char in WHITE_CHARS:
            idx += 1
            value.append(char)
        else:
            string, idx = _parse_unquoted_string(data, idx)
            value.append(string)


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
