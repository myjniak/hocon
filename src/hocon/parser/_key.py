from dataclasses import dataclass

from ._data import ParserInput
from ._eat import eat_comments
from ._quoted_string import parse_quoted_string, parse_triple_quoted_string
from ._unquoted_string import _parse_unquoted_string_key
from ..constants import WHITE_CHARS
from ..exceptions import HOCONDecodeError
from ..strings import UnquotedString


@dataclass
class Keypath:
    keys: list[str]
    end_idx: int
    iadd: bool = False
    include: bool = False


def parse_keypath(data: ParserInput, idx: int = 0, keyend_indicator: str = ":={") -> Keypath:
    keychunks_list: list[list[str]] = [[]]
    while True:
        old_idx = idx
        idx = eat_comments(data, idx)
        string, idx = _parse_key_chunk(data, idx)
        if not keychunks_list[-1] and UnquotedString("include") in string:
            return Keypath(keys=[], end_idx=idx, include=True)
        keychunks_list[-1].append(string)
        char = data[idx]
        if idx == old_idx:
            raise HOCONDecodeError(f"This is an exception preventing infinite loop and it's a bug. Please report it.")
        if data[idx] in keyend_indicator or data[idx : idx + 2] == "+=":
            if isinstance(string, UnquotedString):
                keychunks_list[-1][-1] = keychunks_list[-1][-1].rstrip(WHITE_CHARS)
            keys = ["".join(chunks) for chunks in keychunks_list]
            if char == "{":
                return Keypath(keys, idx)
            if char == "+":
                return Keypath(keys, idx + 2, iadd=True)
            return Keypath(keys, idx + 1)
        if data[idx] == ".":
            idx += 1
            keychunks_list.append([])


def _parse_key_chunk(data: ParserInput, idx: int) -> tuple[str, int]:
    char = data[idx]
    if data[idx : idx + 3] == '"""':
        string, idx = parse_triple_quoted_string(data, idx + 3)
    elif char == '"':
        string, idx = parse_quoted_string(data, idx + 1)
    else:
        return _parse_unquoted_string_key(data, idx)
    return string, idx
