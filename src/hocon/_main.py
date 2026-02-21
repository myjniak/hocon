from pathlib import Path
from typing import TextIO

from .constants import ROOT_TYPE
from .parser import parse
from .resolver import resolve


def load(fp: TextIO) -> ROOT_TYPE:
    """Load HOCON from an open file.

    Relative path for include and encoding is set automatically.
    """
    absolute_path = Path(fp.name).absolute()
    return loads(fp.read(), absolute_path, fp.encoding)


def loads(data: str, root_filepath: str | Path | None = None, encoding: str = "UTF-8") -> ROOT_TYPE:
    """Load a string to HOCON.

    :param data: string to parse and resolve.
    :param root_filepath: path to resolve 'include' from. Set current working directory by default.
    :param encoding: encoding to use for 'include' files.
    :return: resolved dict or list
    """
    root_filepath = root_filepath or Path.cwd() / "application.conf"
    parsed = parse(data, root_filepath=root_filepath, encoding=encoding)
    return resolve(parsed)
