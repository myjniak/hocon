from hocon.constants import ELEMENT_SEPARATORS, WHITE_CHARS
from hocon.exceptions import HOCONUnexpectedBracesError, HOCONUnexpectedSeparatorError

from ._data import ParserInput


def eat_comments(data: ParserInput, idx: int) -> int:
    while True:
        if data[idx] == "#" or data[idx : idx + 2] == "//":
            idx = __eat_until_newline(data, idx) + 1
            idx = eat_whitespace(data, idx)
        else:
            return idx


def eat_whitespace(data: ParserInput, idx: int) -> int:
    while True:
        char = data[idx]
        if char not in WHITE_CHARS:
            return idx
        idx += 1


def eat_whitespace_and_comments(data: ParserInput, idx: int) -> int:
    while True:
        old_idx = idx
        idx = eat_whitespace(data, idx)
        if data[idx] == "#" or data[idx : idx + 2] == "//":
            idx = __eat_until_newline(data, idx) + 1
        if old_idx == idx:
            return idx


def eat_dict_item_separators(data: ParserInput, idx: int) -> tuple[bool, int]:
    return __eat_item_separators(data, idx, "}", "]")


def eat_list_item_separators(data: ParserInput, idx: int) -> tuple[bool, int]:
    return __eat_item_separators(data, idx, "]", "}")


def __eat_until_newline(data: ParserInput, idx: int) -> int:
    while True:
        if data[idx] == "\n":
            return idx
        idx += 1


def __eat_item_separators(data: ParserInput, idx: int, struct_end: str, unexpected_brace: str) -> tuple[bool, int]:
    separators_found = ""
    while True:
        char = data[idx]
        if char == unexpected_brace:
            msg = "Unexpected closure found"
            raise HOCONUnexpectedBracesError(msg)
        if char == struct_end:
            return True, idx
        if char not in ELEMENT_SEPARATORS:
            return bool(separators_found), idx
        separators_found += char
        if separators_found.count(",") > 1:
            msg = "Multiple commas found"
            raise HOCONUnexpectedSeparatorError(msg)
        idx += 1
