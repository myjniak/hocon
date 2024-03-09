from typing import Union

from ._eat import eat_comments
from ._quoted_string import parse_quoted_string, parse_triple_quoted_string
from .constants import UNQUOTED_STR_FORBIDDEN_CHARS, WHITE_CHARS, KEY_VALUE_SEPARATORS
from .exceptions import HOCONDecodeError


def parse_keypath(data: str, idx: int = 0) -> tuple[list[str], int]:
    keys = []
    while True:
        old_idx = idx
        idx = eat_comments(data, idx)
        char = data[idx]
        if data[idx:idx + 3] == "\"\"\"":
            string, idx = parse_triple_quoted_string(data, idx + 3)
        elif char == "\"":
            string, idx = parse_quoted_string(data, idx + 1)
        else:
            string, idx = _parse_unquoted_string_key(data, idx)
        keys.append(string)
        separator_found, idx = _eat_key_value_separator(data, idx)
        if separator_found:
            return keys, idx
        if idx == old_idx:
            raise HOCONDecodeError(f"No key-value separator found for key {''.join(keys)}")
        if data[idx] == ".":
            idx += 1


def _parse_unquoted_string_key(data: str, idx: int) -> tuple[Union[str, list[str]], int]:
    key_endings = UNQUOTED_STR_FORBIDDEN_CHARS + "."
    key = ""
    while True:
        old_idx = idx
        idx = eat_comments(data, idx)
        char = data[idx]
        if char in key_endings or idx != old_idx:
            return key.strip(), idx
        key += char
        idx += 1


def _eat_key_value_separator(data: str, idx: int) -> tuple[bool, int]:
    chars_to_eat = WHITE_CHARS + KEY_VALUE_SEPARATORS
    separator_found = False
    while True:
        char = data[idx]
        if char == "{":
            return True, idx
        if char not in chars_to_eat:
            return separator_found, idx
        if char in KEY_VALUE_SEPARATORS:
            separator_found = True
        idx += 1
