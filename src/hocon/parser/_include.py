from enum import StrEnum, auto
from pathlib import Path

from hocon.exceptions import HOCONIncludeError
from hocon.parser._eat import eat_whitespace_and_comments
from hocon.parser._quoted_string import parse_quoted_string
from hocon.parser.data import ParserInput


class IncludeMode(StrEnum):
    """See https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-syntax."""

    FILE = auto()
    CLASSPATH = auto()
    URL = auto()
    DEFAULT = auto()


def parse_include_value(data: ParserInput, idx: int) -> tuple[ParserInput, int]:
    required: bool = False
    if data[idx : idx + 8] == "required":
        required = True
        idx += 8
        if data[idx] != "(":
            msg = "Missing '(' bracket in required function!"
            raise HOCONIncludeError(msg, data, idx)
        idx += 1
    include_mode, idx = _read_mode(data, idx)
    if data[idx : idx + 3] == '"""' or data[idx] != '"':
        msg = "Only single quoted include filepaths are supported."
        raise HOCONIncludeError(msg, data, idx)
    string, idx = parse_quoted_string(data, idx + 1)
    idx = _eat_closing_brackets(data, idx, include_mode, required=required)
    content = load_include_content(data, string, include_mode, required=required)
    return content, idx


def load_include_content(data: ParserInput, string: str, mode: IncludeMode, *, required: bool) -> ParserInput:
    if mode in {IncludeMode.FILE, IncludeMode.DEFAULT}:
        external_filepath = Path(data.absolute_filepath).parent / string
        if not required and not external_filepath.exists():
            external_data = "{}"
        else:
            external_data = external_filepath.read_text(encoding=data.encoding)
        external_input = ParserInput(data=external_data, absolute_filepath=external_filepath, encoding=data.encoding)
        ext_idx = eat_whitespace_and_comments(external_input, 0)
        if external_input[ext_idx] == "[":
            msg = f"An included file '{string}' must contain an object, not an array."
            raise HOCONIncludeError(msg)
        return external_input
    msg = f"Include {mode=} not implemented"
    raise NotImplementedError(msg)


def _eat_closing_brackets(data: ParserInput, idx: int, include_mode: IncludeMode, *, required: bool) -> int:
    if include_mode != IncludeMode.DEFAULT:
        idx = _eat_closing_bracket(data, idx)
    if required:
        idx = _eat_closing_bracket(data, idx)
    return idx


def _eat_closing_bracket(data: ParserInput, idx: int) -> int:
    if data[idx] == ")":
        return idx + 1
    msg = "Missing closing ')' bracket in include statement!"
    raise HOCONIncludeError(msg, data, idx)


def _read_mode(data: ParserInput, idx: int) -> tuple[IncludeMode, int]:
    for mode in IncludeMode:
        mode_len = len(str(mode))
        if data[idx : idx + mode_len] != mode:
            continue
        idx += mode_len
        if data[idx] != "(":
            msg = "Missing '(' bracket!"
            raise HOCONIncludeError(msg, data, idx)
        idx += 1
        break
    else:
        mode = IncludeMode.DEFAULT
    if data[idx] == '"':
        return mode, idx
    msg = "Unsupported include syntax!"
    raise HOCONIncludeError(msg, data, idx)
