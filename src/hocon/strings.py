"""Hocon needs to distinguish "quoted" from unquoted strings."""

from hocon.constants import WHITE_CHARS


class QuotedString(str):

    __slots__ = ()


class UnquotedString(str):

    __slots__ = ()

    def is_empty(self) -> bool:
        """Is given value an UnquotedString containing nothing or WHITE_CHARS only."""
        return not self.strip(WHITE_CHARS)
