from .constants import INLINE_WHITE_CHARS, WHITE_CHARS, ELEMENT_SEPARATORS
from .exceptions import HOCONUnexpectedBracesError


def eat_comments(data: str, idx: int) -> int:
    while True:
        if data[idx] == "#" or data[idx:idx + 2] == "//":
            idx = eat_until_newline(data, idx) + 1
            idx = eat_whitespace(data, idx)
        else:
            return idx


def eat_inline_whitespace(data: str, idx: int) -> int:
    while True:
        char = data[idx]
        if char not in INLINE_WHITE_CHARS:
            return idx
        idx += 1


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
            idx = eat_until_newline(data, idx) + 1
        if old_idx == idx:
            return idx


def eat_dict_item_separators(data: str, idx: int) -> tuple[bool, int]:
    chars_to_eat = WHITE_CHARS + ELEMENT_SEPARATORS
    separator_found = False
    while True:
        char = data[idx]
        if char == "]":
            raise HOCONUnexpectedBracesError("Unexpected list closure found")
        if char == "}":
            return True, idx
        if char not in chars_to_eat:
            return separator_found, idx
        if char in ELEMENT_SEPARATORS:
            separator_found = True
        idx += 1


def eat_list_item_separators(data: str, idx: int) -> tuple[bool, int]:
    chars_to_eat = WHITE_CHARS + ELEMENT_SEPARATORS
    separator_found = False
    while True:
        char = data[idx]
        if char == "}":
            raise HOCONUnexpectedBracesError("Unexpected dictionary closure found")
        if char == "]":
            return True, idx
        if char not in chars_to_eat:
            return separator_found, idx
        if char in ELEMENT_SEPARATORS:
            separator_found = True
        idx += 1


def eat_until_newline(data: str, idx: int) -> int:
    while True:
        if data[idx] == "\n":
            return idx
        idx += 1
