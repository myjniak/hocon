from dataclasses import dataclass
from pathlib import Path

from hocon.exceptions import HOCONIncludeError
from hocon.parser._data import ParserInput
from hocon.parser._quoted_string import parse_quoted_string


@dataclass
class IncludeFile:
    path: Path
    required: bool = False


def parse_include_value(data: ParserInput, idx: int) -> tuple[IncludeFile, int]:
    required: bool = False
    if data[idx : idx + 8] == "required":
        required = True
        idx += 8
        if data[idx] != "(":
            msg = "Missing '(' bracket in required function!"
            raise HOCONIncludeError(msg)
        idx += 1
    if data[idx : idx + 3] == '"""' or data[idx] != '"':
        msg = "Only single quoted include filepaths are supported."
        raise HOCONIncludeError(msg)
    string, idx = parse_quoted_string(data, idx + 1)
    if required:
        if data[idx] == ")":
            idx += 1
        else:
            msg = f"Missing ')' bracket in required function when including {string}"
            raise HOCONIncludeError(msg)
    external_filepath = Path(data.absolute_filepath).parent / string
    return IncludeFile(path=external_filepath, required=required), idx
