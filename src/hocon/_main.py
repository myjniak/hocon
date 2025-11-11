from pathlib import Path
from typing import TextIO

from .constants import ROOT_TYPE
from .parser import parse
from .resolver import resolve


def load(fp: TextIO) -> ROOT_TYPE:
    absolute_path = Path.cwd() / fp.name
    return loads(fp.read(), absolute_path, fp.encoding)


def loads(data: str, root_filepath: str | Path | None = None, encoding: str = "UTF-8") -> ROOT_TYPE:
    root_filepath = root_filepath or Path.cwd()
    parsed = parse(data, root_filepath=root_filepath, encoding=encoding)
    return resolve(parsed)
