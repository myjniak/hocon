import json
import os
from typing import IO
from pathlib import Path
from .constants import ROOT_TYPE
from .exceptions import HOCONNoDataError, HOCONExcessiveDataError
from .parser._eat import eat_whitespace_and_comments, eat_whitespace, eat_comments
from .parser._parser import parse_list, parse_dict
from .resolver._resolver import resolve
from .parser._data import ParserInput


def load(fp: IO) -> ROOT_TYPE:
    absolute_path = Path(os.path.join(os.getcwd(), fp.name))
    return loads(fp.read(), absolute_path)


def loads(data: str, root_filepath: str | os.PathLike = os.getcwd()) -> ROOT_TYPE:
    parsed = parse(data, root_filepath=root_filepath)
    resolved = resolve(parsed)
    return resolved


def parse(data: str, root_filepath: str | os.PathLike = os.getcwd()) -> ROOT_TYPE:
    if not data:
        raise HOCONNoDataError("Empty string provided")
    data_object = ParserInput(data, Path(root_filepath))
    result: ROOT_TYPE
    idx = eat_whitespace_and_comments(data_object, 0)
    if data[idx] == "[":
        result, idx = parse_list(data_object, idx=idx + 1)
    elif data[idx] == "{":
        result, idx = parse_dict(data_object, idx=idx + 1)
    else:
        data_object.data += "\n}"
        result, idx = parse_dict(data_object, idx=idx)
    __assert_no_content_left(data_object, idx)
    return result


def dumps(hocon_: ROOT_TYPE) -> str:
    return json.dumps(hocon_)


def __assert_no_content_left(data: ParserInput, idx: int) -> None:
    try:
        while True:
            old_idx = idx
            idx = eat_whitespace(data, idx)
            idx = eat_comments(data, idx)
            if idx == old_idx:
                raise HOCONExcessiveDataError("Excessive meaningful data outside of the HOCON structure.")
    except IndexError:
        return
