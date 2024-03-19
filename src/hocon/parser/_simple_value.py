import re
from typing import Union

from ._eat import eat_comments
from ._quoted_string import parse_triple_quoted_string, parse_quoted_string
from hocon.constants import SIMPLE_VALUE_TYPE, ELEMENT_SEPARATORS, SECTION_CLOSURES, WHITE_CHARS, \
    UNQUOTED_STR_FORBIDDEN_CHARS, _FLOAT_CONSTANTS, NUMBER_RE
from hocon.exceptions import HOCONUnexpectedSeparatorError, HOCONUnquotedStringError, HOCONUnexpectedBracesError


def parse_simple_value(data: str, idx: int = 0) -> tuple[SIMPLE_VALUE_TYPE, int, bool]:
    values = []
    contains_quoted_string = False
    newline_found = False
    while True:
        char = data[idx]
        if char == "," and not values:
            raise HOCONUnexpectedSeparatorError("Unexpected ',' found.")
        if char in ELEMENT_SEPARATORS + SECTION_CLOSURES or newline_found:
            if not values:
                raise HOCONUnexpectedBracesError("Unexpected closure")
            stripped_values = _strip_string_list(values)
            joined = "".join(stripped_values)
            if len(stripped_values) == 1 and not contains_quoted_string:
                return _cast_string_value(joined), idx, newline_found
            return joined, idx, newline_found
        if data[idx:idx + 3] == "\"\"\"":
            contains_quoted_string = True
            string, idx = parse_triple_quoted_string(data, idx + 3)
            values.append(string)
        elif char == "\"":
            contains_quoted_string = True
            string, idx = parse_quoted_string(data, idx + 1)
            values.append(string)
        elif char in WHITE_CHARS:
            idx += 1
            values.append(char)
        else:
            string, idx, newline_found = _parse_unquoted_string(data, idx)
            values.append(string)


def _strip_string_list(values: list[str]) -> list[str]:
    first = next(index for index, value in enumerate(values) if value.strip())
    last = -1 * next(index for index, value in enumerate(reversed(values)) if value.strip())
    if last == 0:
        return values[first:]
    return values[first:last]


def _parse_unquoted_string(data: str, idx: int) -> tuple[str, int, bool]:
    unquoted_string_end = UNQUOTED_STR_FORBIDDEN_CHARS + WHITE_CHARS
    string = ""
    while True:
        char = data[idx]
        old_idx = idx
        idx = eat_comments(data, idx)
        if idx != old_idx:
            return string.strip(), idx, idx != old_idx
        if char in unquoted_string_end:
            if not string:
                raise HOCONUnquotedStringError("Error when parsing unquoted string")
            return string.strip(), idx, idx != old_idx
        string += char
        idx += 1


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
