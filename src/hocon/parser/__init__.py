"""Read hocon data file with raw string into a structure of parsed (unresolved!) objects."""

from ._data import ParserInput
from ._parser import parse

__all__ = ("ParserInput", "parse")
