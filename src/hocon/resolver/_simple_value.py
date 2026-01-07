import re

from hocon.constants import _FLOAT_CONSTANTS, NUMBER_RE, SIMPLE_VALUE_TYPE, WHITE_CHARS
from hocon.strings import QuotedString, UnquotedString


def resolve_simple_value(chunks: list[str], *, strip_left: bool = True, strip_right: bool = True) -> SIMPLE_VALUE_TYPE:
    chunks = _strip_string_list(chunks, left=strip_left, right=strip_right)
    joined = "".join(chunks)
    if len(chunks) == 1 and isinstance(chunks[0], UnquotedString):
        return _cast_string_value(joined)
    return joined


def _strip_string_list(values: list[str], *, left: bool = True, right: bool = True) -> list[str]:
    if left:
        first = next(
            index for index, value in enumerate(values) if value.strip(WHITE_CHARS) or isinstance(value, QuotedString)
        )
    else:
        first = 0
    if right:
        last = -1 * next(
            index
            for index, value in enumerate(reversed(values))
            if value.strip(WHITE_CHARS) or isinstance(value, QuotedString)
        )
    else:
        last = 0
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
    if string in _FLOAT_CONSTANTS:
        return _FLOAT_CONSTANTS[string]
    match = re.match(NUMBER_RE, string)
    if match is not None and match.group() == string:
        return _cast_to_number(string)
    return string


def _cast_to_number(string: str) -> float | int:
    if string.lstrip("-").isdigit():
        return int(string)
    return float(string)
