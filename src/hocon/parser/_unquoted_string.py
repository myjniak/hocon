from hocon.constants import WHITE_CHARS, UNQUOTED_STR_FORBIDDEN_CHARS, SECTION_OPENING
from hocon.exceptions import HOCONUnquotedStringError, HOCONUnexpectedSeparatorError, HOCONInvalidKeyError
from hocon.strings import UnquotedString


def _parse_unquoted_string_value(data: str, idx: int) -> tuple[UnquotedString, int]:
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


def _parse_unquoted_string_key(data: str, idx: int) -> tuple[str, int]:
    string_end = UNQUOTED_STR_FORBIDDEN_CHARS + "."
    string = ""
    while True:
        char = data[idx]
        if char in string_end or data[idx:idx + 2] == "//":
            if not string:
                _raise_parse_key_exception(data, idx)
            return string, idx
        string += char
        idx += 1


def _raise_parse_key_exception(data: str, idx: int):
    if data[idx] == ",":
        raise HOCONUnexpectedSeparatorError("Excessive leading comma found in a dictionary.")
    if data[idx] in "{[":
        raise HOCONInvalidKeyError("Objects and arrays do not make sense as field keys.")
    raise HOCONInvalidKeyError("Dictionary started with an invalid character.")
