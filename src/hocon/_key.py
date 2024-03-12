from typing import Union

from ._eat import eat_comments, eat_whitespace
from ._quoted_string import parse_quoted_string, parse_triple_quoted_string
from .constants import UNQUOTED_STR_FORBIDDEN_CHARS, KEY_VALUE_SEPARATORS
from .exceptions import HOCONDecodeError, HOCONUnexpectedSeparatorError, HOCONInvalidKeyError


def parse_keypath(data: str, idx: int = 0) -> tuple[list[str], int]:
    keychunks_list: list[list[str]] = [[]]
    while True:
        old_idx = idx
        idx = eat_comments(data, idx)
        string, idx, keychunk_is_unquoted = _parse_key_chunk(data, idx)
        keychunks_list[-1].append(string)
        char = data[idx]
        if idx == old_idx:
            keys = ["".join(chunks) for chunks in keychunks_list]
            _raise_keypath_exception(data, idx, keys)
        if char in KEY_VALUE_SEPARATORS or char == "{":
            if keychunk_is_unquoted:
                keychunks_list[-1][-1] = keychunks_list[-1][-1].rstrip()
            keys = ["".join(chunks) for chunks in keychunks_list]
            if char == "{":
                return keys, idx
            idx = eat_whitespace(data, idx + 1)
            return keys, idx
        if data[idx] == ".":
            idx += 1
            keychunks_list.append([])


def _raise_keypath_exception(data: str, idx: int, keys: list[str]):
    if "".join(keys).strip():
        raise HOCONDecodeError(f"No key-value separator found for key {''.join(keys)}")
    if data[idx] == ",":
        raise HOCONUnexpectedSeparatorError("Excessive leading dict field separator found.")
    if data[idx] in "{[":
        raise HOCONInvalidKeyError("Objects and arrays do not make sense as field keys.")
    raise HOCONInvalidKeyError("Dictionary started with an invalid character.")


def _parse_key_chunk(data: str, idx: int) -> tuple[str, int, bool]:
    char = data[idx]
    if data[idx:idx + 3] == "\"\"\"":
        string, idx = parse_triple_quoted_string(data, idx + 3)
    elif char == "\"":
        string, idx = parse_quoted_string(data, idx + 1)
    else:
        string, idx = _parse_unquoted_string_key(data, idx)
        return string, idx, True
    return string, idx, False


def _parse_unquoted_string_key(data: str, idx: int) -> tuple[Union[str, list[str]], int]:
    key_endings = UNQUOTED_STR_FORBIDDEN_CHARS + "."
    key = ""
    while True:
        old_idx = idx
        idx = eat_comments(data, idx)
        char = data[idx]
        if char in key_endings or idx != old_idx:
            return key, idx
        key += char
        idx += 1
