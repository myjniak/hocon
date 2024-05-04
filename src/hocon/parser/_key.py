from ..constants import KEY_VALUE_SEPARATORS, WHITE_CHARS
from ..exceptions import HOCONDecodeError
from ._eat import eat_comments
from ._quoted_string import parse_quoted_string, parse_triple_quoted_string
from ._unquoted_string import _parse_unquoted_string_key
from ..strings import QuotedString, UnquotedString


def parse_keypath(data: str, idx: int = 0, keyend_indicator: str = KEY_VALUE_SEPARATORS + "{") -> tuple[list[str], int]:
    keychunks_list: list[list[str]] = [[]]
    while True:
        old_idx = idx
        idx = eat_comments(data, idx)
        string, idx = _parse_key_chunk(data, idx)
        keychunks_list[-1].append(string)
        char = data[idx]
        if idx == old_idx:
            raise HOCONDecodeError(f"This is an exception preventing infinite loop and it's a bug. Please report it.")
        if char in keyend_indicator:
            if isinstance(string, UnquotedString):
                keychunks_list[-1][-1] = keychunks_list[-1][-1].rstrip(WHITE_CHARS)
            keys = ["".join(chunks) for chunks in keychunks_list]
            if char == "{":
                return keys, idx
            return keys, idx + 1
        if data[idx] == ".":
            idx += 1
            keychunks_list.append([])


def _parse_key_chunk(data: str, idx: int) -> tuple[str, int]:
    char = data[idx]
    if data[idx:idx + 3] == "\"\"\"":
        string, idx = parse_triple_quoted_string(data, idx + 3)
    elif char == "\"":
        string, idx = parse_quoted_string(data, idx + 1)
    else:
        return _parse_unquoted_string_key(data, idx)
    return string, idx
