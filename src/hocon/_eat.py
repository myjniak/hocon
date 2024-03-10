from .constants import INLINE_WHITE_CHARS, WHITE_CHARS, ELEMENT_SEPARATORS
from .exceptions import HOCONUnexpectedBracesError, HOCONUnexpectedSeparatorError


def eat_comments(data: str, idx: int) -> int:
    while True:
        if data[idx] == "#" or data[idx:idx + 2] == "//":
            idx = __eat_until_newline(data, idx) + 1
            idx = eat_whitespace(data, idx)
        else:
            return idx


def eat_whitespace(data: str, idx: int) -> int:
    while True:
        char = data[idx]
        if char not in WHITE_CHARS:
            return idx
        idx += 1


def eat_whitespace_and_comments(data: str, idx: int) -> int:
    while True:
        old_idx = idx
        idx = eat_whitespace(data, idx)
        if data[idx] == "#" or data[idx:idx+2] == "//":
            idx = __eat_until_newline(data, idx) + 1
        if old_idx == idx:
            return idx


def eat_dict_item_separators(data: str, idx: int) -> tuple[bool, int]:
    return __eat_item_separators(data, idx, "}", "]")


def eat_list_item_separators(data: str, idx: int) -> tuple[bool, int]:
    return __eat_item_separators(data, idx, "]", "}")


def __eat_until_newline(data: str, idx: int) -> int:
    while True:
        if data[idx] == "\n":
            return idx
        idx += 1


def __eat_item_separators(data: str, idx: int, struct_end: str, unexpected_brace: str) -> tuple[bool, int]:
    chars_to_eat = WHITE_CHARS + ELEMENT_SEPARATORS
    separators_found = ""
    while True:
        char = data[idx]
        if char == unexpected_brace:
            raise HOCONUnexpectedBracesError("Unexpected closure found")
        if char == struct_end:
            return True, idx
        if char not in chars_to_eat:
            return bool(separators_found), idx
        if char in ELEMENT_SEPARATORS:
            separators_found += char
        if separators_found.count(",") > 1:
            raise HOCONUnexpectedSeparatorError("Multiple commas found")
        idx += 1
