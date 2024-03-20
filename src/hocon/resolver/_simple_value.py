import re
from typing import Union

from hocon.constants import SIMPLE_VALUE_TYPE, _FLOAT_CONSTANTS, NUMBER_RE
from hocon.strings import QuotedString, UnquotedString


def resolve_simple_value(chunks: list[str]) -> SIMPLE_VALUE_TYPE:
    stripped_values = _strip_string_list(chunks)
    joined = "".join(stripped_values)
    if len(stripped_values) == 1 and isinstance(stripped_values[0], UnquotedString):
        return _cast_string_value(joined)
    return joined


def _strip_string_list(values: list[str]) -> list[str]:
    first = next(index for index, value in enumerate(values) if value.strip() or isinstance(value, QuotedString))
    last = -1 * next(index for index, value in enumerate(reversed(values)) if value.strip() or isinstance(value, QuotedString))
    if last == 0:
        return values[first:]
    return values[first:last]


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
