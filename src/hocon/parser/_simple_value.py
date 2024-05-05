from typing import Union

from ..constants import ELEMENT_SEPARATORS, SECTION_CLOSING, INLINE_WHITE_CHARS
from ..exceptions import HOCONUnexpectedSeparatorError, HOCONUnexpectedBracesError
from ._key import parse_keypath
from ._quoted_string import parse_triple_quoted_string, parse_quoted_string
from ._unquoted_string import _parse_unquoted_string_value
from ..strings import UnquotedString, QuotedString
from ..unresolved import UnresolvedSubstitution


def parse_simple_value(data: str, idx: int = 0) -> tuple[Union[UnquotedString, QuotedString, UnresolvedSubstitution], int]:
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
    elif data[idx:idx + 2] == "${":
        return _parse_substitution(data, idx + 2)
    else:
        return _parse_unquoted_string_value(data, idx)


def _parse_whitespace_chunk(data: str, idx: int) -> tuple[UnquotedString, int]:
    string = ""
    while True:
        char = data[idx]
        if char not in INLINE_WHITE_CHARS:
            return UnquotedString(string), idx
        string += char
        idx += 1


def _parse_substitution(data: str, idx: int) -> tuple[UnresolvedSubstitution, int]:
    if data[idx] == "?":
        optional = True
        idx += 1
    else:
        optional = False
    keypath = parse_keypath(data, idx, keyend_indicator="}")
    substitution = UnresolvedSubstitution(keypath.keys, optional)
    return substitution, keypath.end_idx
