from ._data import ParserInput
from ..constants import WHITE_CHARS, UNQUOTED_STR_FORBIDDEN_CHARS, SECTION_OPENING
from ..exceptions import HOCONUnquotedStringError, HOCONUnexpectedSeparatorError, HOCONInvalidKeyError
from ..strings import UnquotedString


def _parse_unquoted_string_value(data: ParserInput, idx: int) -> tuple[UnquotedString, int]:
    unquoted_string_end = UNQUOTED_STR_FORBIDDEN_CHARS + WHITE_CHARS
    string = ""
    while True:
        char = data[idx]
        if char in SECTION_OPENING:
            raise HOCONUnquotedStringError(f"Forbidden opening '{char}' found when parsing unquoted string.")
        if char in unquoted_string_end or data[idx:idx + 2] == "//":
            if not string:
                raise HOCONUnquotedStringError("Error when parsing unquoted string")
            return UnquotedString(string), idx
        string += char
        idx += 1


def _parse_unquoted_string_key(data: ParserInput, idx: int) -> tuple[UnquotedString, int]:
    string_end = UNQUOTED_STR_FORBIDDEN_CHARS + "."
    string = ""
    while True:
        char = data[idx]
        if char == "\n":
            raise HOCONInvalidKeyError("Encountered newline before key-value separator.")
        if char in string_end or data[idx:idx + 2] == "//":
            if not string:
                _raise_parse_key_exception(data, idx)
            return UnquotedString(string), idx
        string += char
        idx += 1


def _raise_parse_key_exception(data: ParserInput, idx: int):
    if data[idx] == ",":
        raise HOCONUnexpectedSeparatorError("Excessive leading comma found in a dictionary.")
    if data[idx] in "{[":
        raise HOCONInvalidKeyError("Objects and arrays do not make sense as field keys.")
    if data[idx] == ".":
        raise HOCONInvalidKeyError("Keypath separator '.' used in an invalid way.")
    raise HOCONInvalidKeyError(f"Unexpected character found when parsing keypath: '{data[idx]}'")
