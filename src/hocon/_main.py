import json
import os
from pathlib import Path
from typing import TextIO

from .constants import ROOT_TYPE
from .exceptions import HOCONNoDataError
from .parser._data import ParserInput
from .parser._eat import eat_whitespace_and_comments
from .parser._parser import parse_list, parse_dict, _assert_no_content_left
from .resolver._resolver import resolve


def load(fp: TextIO) -> ROOT_TYPE:
    absolute_path = Path(os.path.join(os.getcwd(), fp.name))
    return loads(fp.read(), absolute_path, fp.encoding)


def loads(data: str, root_filepath: str | os.PathLike = os.getcwd(), encoding: str = "UTF-8") -> ROOT_TYPE:
    parsed = parse(data, root_filepath=root_filepath, encoding=encoding)
    resolved = resolve(parsed)
    return resolved


def parse(data: str, root_filepath: str | os.PathLike = os.getcwd(), encoding: str = "UTF-8") -> ROOT_TYPE:
    if not data:
        raise HOCONNoDataError("Empty string provided")
    data_object = ParserInput(data, Path(root_filepath), encoding=encoding)
    result: ROOT_TYPE
    idx = eat_whitespace_and_comments(data_object, 0)
    if data[idx] == "[":
        result, idx = parse_list(data_object, idx=idx + 1)
    elif data[idx] == "{":
        result, idx = parse_dict(data_object, idx=idx + 1)
    else:
        data_object.data += "\n}"
        result, idx = parse_dict(data_object, idx=idx)
    _assert_no_content_left(data_object, idx)
    return result


def dumps(hocon_: ROOT_TYPE) -> str:
    return json.dumps(hocon_)
