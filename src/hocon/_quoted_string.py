from json import JSONDecoder


def parse_quoted_string(data: str, idx: int) -> tuple[str, int]:
    string, idx = JSONDecoder().parse_string(data, idx)
    return string, idx


def parse_triple_quoted_string(data: str, idx: int) -> tuple[str, int]:
    string = ""
    while True:
        if data[idx:idx + 3] != "\"\"\"":
            string += data[idx]
            idx += 1
            continue
        while True:
            if data[idx + 1:idx + 4] != "\"\"\"":
                return string, idx + 3
            string += data[idx]
            idx += 1
