from json import JSONDecoder

from hocon.strings import QuotedString


def parse_quoted_string(data: str, idx: int) -> tuple[QuotedString, int]:
    string, idx = JSONDecoder().parse_string(data, idx)
    return QuotedString(string), idx


def parse_triple_quoted_string(data: str, idx: int) -> tuple[QuotedString, int]:
    string = ""
    while True:
        if data[idx:idx + 3] != "\"\"\"":
            string += data[idx]
            idx += 1
            continue
        while True:
            if data[idx + 1:idx + 4] != "\"\"\"":
                return QuotedString(string), idx + 3
            string += data[idx]
            idx += 1
