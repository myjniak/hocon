from typing import Union

from ._quoted_string import parse_quoted_string, parse_triple_quoted_string
from .constants import UNQUOTED_STR_FORBIDDEN_CHARS, WHITE_CHARS, KEY_VALUE_SEPARATORS


def parse_keypath(data: str, idx: int = 0) -> tuple[list[str], int]:
    keys = []
    while True:
        char = data[idx]
        if data[idx:idx + 3] == "\"\"\"":
            string, idx = parse_triple_quoted_string(data, idx + 3)
        elif char == "\"":
            string, idx = parse_quoted_string(data, idx + 1)
        else:
            string, idx = _parse_unquoted_string_key(data, idx)
        keys.append(string)
        key_ended, idx = _eat_key_value_separator(data, idx)
        if key_ended:
            return keys, idx
        if data[idx] == ".":
            idx += 1


def _parse_unquoted_string_key(data: str, idx: int) -> tuple[Union[str, list[str]], int]:
    unquoted_key_end = UNQUOTED_STR_FORBIDDEN_CHARS + WHITE_CHARS + "."
    key = data[idx]
    while True:
        idx += 1
        char = data[idx]
        if char not in unquoted_key_end:
            key += char
        else:
            return key.strip(), idx


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
