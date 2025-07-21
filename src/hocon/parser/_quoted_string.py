from json import JSONDecoder

from ._data import ParserInput
from ..strings import QuotedString


def parse_quoted_string(data: ParserInput, idx: int) -> tuple[QuotedString, int]:
    string, idx = JSONDecoder().parse_string(data.data, idx)
    return QuotedString(string), idx


def parse_triple_quoted_string(data: ParserInput, idx: int) -> tuple[QuotedString, int]:
    string = ""
    while True:
        if data[idx : idx + 3] == '"""':
            break
        else:
            string += data[idx]
            idx += 1
    while True:
        if data[idx + 1 : idx + 4] != '"""':
            return QuotedString(string), idx + 3
        string += data[idx]
        idx += 1
