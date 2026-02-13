from hocon.constants import SECTION_OPENING, UNQUOTED_STR_FORBIDDEN_CHARS, WHITE_CHARS
from hocon.exceptions import (
    HOCONInvalidKeyError,
    HOCONUnexpectedSeparatorError,
    HOCONUnquotedStringError,
)
from hocon.strings import UnquotedString

from .data import ParserInput


def _parse_unquoted_string_value(data: ParserInput, idx: int) -> tuple[UnquotedString, int]:
    unquoted_string_end = UNQUOTED_STR_FORBIDDEN_CHARS + WHITE_CHARS
    string = ""
    while True:
        char = data[idx]
        if char in SECTION_OPENING:
            msg = f"Forbidden opening '{char}' found when parsing unquoted string."
            raise HOCONUnquotedStringError(msg)
        if char in unquoted_string_end or data[idx : idx + 2] == "//":
            if not string:
                msg = "Error when parsing unquoted string"
                raise HOCONUnquotedStringError(msg, data, idx)
            return UnquotedString(string), idx
        string += char
        idx += 1


def _parse_unquoted_string_key(data: ParserInput, idx: int) -> tuple[UnquotedString, int]:
    string_end = UNQUOTED_STR_FORBIDDEN_CHARS + "."
    string = ""
    while True:
        char = data[idx]
        if string == "include":
            return UnquotedString(string), idx
        if char in string_end or data[idx : idx + 2] == "//":
            if not string:
                _raise_parse_key_exception(data, idx)
            return UnquotedString(string), idx
        string += char
        idx += 1


def _raise_parse_key_exception(data: ParserInput, idx: int) -> None:
    if data[idx] == ",":
        msg = "Excessive leading comma found in a dictionary"
        raise HOCONUnexpectedSeparatorError(msg, data, idx)
    if data[idx] in "{[":
        msg = "Objects and arrays do not make sense as field keys"
        raise HOCONInvalidKeyError(msg, data, idx)
    if data[idx] == ".":
        msg = "Keypath separator '.' used in an invalid way"
        raise HOCONInvalidKeyError(msg, data, idx)
    if idx == len(data.data) - 1:
        msg = "Unexpected EOF while parsing keypath"
    else:
        msg = "Unexpected character found when parsing keypath"
    raise HOCONInvalidKeyError(msg, data, idx)
