import os
from pathlib import Path
from typing import TextIO

from .constants import ROOT_TYPE
from .parser import parse
from .resolver import resolve


def load(fp: TextIO) -> ROOT_TYPE:
    absolute_path = Path(os.path.join(os.getcwd(), fp.name))
    return loads(fp.read(), absolute_path, fp.encoding)


def loads(data: str, root_filepath: str | Path = os.getcwd(), encoding: str = "UTF-8") -> ROOT_TYPE:
    parsed = parse(data, root_filepath=root_filepath, encoding=encoding)
    return resolve(parsed)
