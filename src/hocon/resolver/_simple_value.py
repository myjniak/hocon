import re

from hocon.constants import _FLOAT_CONSTANTS, NUMBER_RE, SIMPLE_VALUE_TYPE, WHITE_CHARS
from hocon.strings import HOCON_STRING, QuotedString, UnquotedString


def resolve_simple_value(chunks: list[HOCON_STRING]) -> SIMPLE_VALUE_TYPE:
    chunks = _strip_string_list(chunks)
    if len(chunks) == 1 and isinstance(chunks[0], UnquotedString):
        return cast_string_value(str(chunks[0]))
    return "".join(list(map(str, chunks)))


def _strip_string_list(values: list[HOCON_STRING]) -> list[HOCON_STRING]:
    first = next(
        index for index, value in enumerate(values) if value.strip(WHITE_CHARS) or isinstance(value, QuotedString)
    )
    last = -1 * next(
        index
        for index, value in enumerate(reversed(values))
        if value.strip(WHITE_CHARS) or isinstance(value, QuotedString)
    )
    if last == 0:
        return values[first:]
    return values[first:last]


def cast_string_value(string: str) -> SIMPLE_VALUE_TYPE:
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
