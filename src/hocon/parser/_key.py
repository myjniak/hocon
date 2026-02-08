from dataclasses import dataclass

from hocon.constants import WHITE_CHARS
from hocon.strings import UnquotedString

from ._eat import eat_comments
from ._quoted_string import parse_quoted_string, parse_triple_quoted_string
from ._unquoted_string import _parse_unquoted_string_key
from .data import ParserInput


@dataclass
class Keypath:
    """Used when parsing keypath of the hocon tree and in substitution target keypath."""

    keys: list[str]
    end_idx: int
    iadd: bool = False
    include: bool = False


def parse_keypath(data: ParserInput, idx: int = 0, keyend_indicator: str = ":={") -> Keypath:
    keychunks_list: list[list[str]] = [[]]
    while True:
        idx = eat_comments(data, idx)
        string, idx = _parse_key_chunk(data, idx)
        if not keychunks_list[-1] and string.startswith("include") and type(string) is UnquotedString:
            return Keypath(keys=[], end_idx=idx, include=True)
        keychunks_list[-1].append(string)
        char = data[idx]
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
