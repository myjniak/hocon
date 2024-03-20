from typing import Union

from hocon.constants import ELEMENT_SEPARATORS, SECTION_CLOSING, WHITE_CHARS, \
    UNQUOTED_STR_FORBIDDEN_CHARS, INLINE_WHITE_CHARS, SECTION_OPENING
from hocon.exceptions import HOCONUnexpectedSeparatorError, HOCONUnquotedStringError, HOCONUnexpectedBracesError
from ._quoted_string import parse_triple_quoted_string, parse_quoted_string
from ..strings import UnquotedString, QuotedString


def parse_simple_value(data: str, idx: int = 0) -> tuple[Union[UnquotedString, QuotedString], int]:
    char = data[idx]
    if char == ",":
        raise HOCONUnexpectedSeparatorError("Unexpected ',' found.")
    if char in ELEMENT_SEPARATORS + SECTION_CLOSING:
        raise HOCONUnexpectedBracesError("Unexpected closure")
    if data[idx:idx + 3] == "\"\"\"":
        return parse_triple_quoted_string(data, idx + 3)
    elif char == "\"":
        return parse_quoted_string(data, idx + 1)
    elif char in INLINE_WHITE_CHARS:
        return _parse_whitespace_chunk(data, idx)
    else:
        return _parse_unquoted_string(data, idx)


def _parse_whitespace_chunk(data: str, idx: int) -> tuple[UnquotedString, int]:
    string = ""
    while True:
        char = data[idx]
        if char not in INLINE_WHITE_CHARS:
            return UnquotedString(string), idx
        string += char
        idx += 1


def _parse_unquoted_string(data: str, idx: int) -> tuple[UnquotedString, int]:
    unquoted_string_end = UNQUOTED_STR_FORBIDDEN_CHARS + WHITE_CHARS
    string = ""
    while True:
        char = data[idx]
        if char in SECTION_OPENING:
            raise HOCONUnquotedStringError(f"Forbidden opening '{char}' found when parsing unquoted string")
        if char in unquoted_string_end or data[idx:idx + 2] == "//":
            if not string:
                raise HOCONUnquotedStringError("Error when parsing unquoted string")
            return UnquotedString(string), idx
        string += char
        idx += 1
