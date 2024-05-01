import json
from typing import Union

from .constants import ROOT_TYPE
from .parser._eat import eat_whitespace_and_comments, eat_whitespace, eat_comments
from .parser._parser import parse_list, parse_dict
from .exceptions import HOCONNoDataError, HOCONExcessiveDataError
from .resolver._resolver import resolve


def loads(data: str) -> ROOT_TYPE:
    parsed = parse(data)
    resolved = resolve(parsed)
    return resolved


def parse(data: str) -> ROOT_TYPE:
    if not data:
        raise HOCONNoDataError("Empty string provided")
    result: ROOT_TYPE
    idx = eat_whitespace_and_comments(data, 0)
    if data[idx] == "[":
        result, idx = parse_list(data, idx=idx + 1)
    elif data[idx] == "{":
        result, idx = parse_dict(data, idx=idx + 1)
    else:
        data += "\n}"
        result, idx = parse_dict(data, idx=idx)
    __assert_no_content_left(data, idx)
    return result


def dumps(hocon_: ROOT_TYPE) -> str:
    return json.dumps(hocon_)


def __assert_no_content_left(data: str, idx: int) -> None:
    try:
        while True:
            old_idx = idx
            idx = eat_whitespace(data, idx)
            idx = eat_comments(data, idx)
            if idx == old_idx:
                raise HOCONExcessiveDataError("Excessive meaningful data outside of the HOCON structure.")
    except IndexError:
        return
