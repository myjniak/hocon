"""Hocon needs to distinguish "quoted" from unquoted strings."""

from hocon.constants import WHITE_CHARS


class QuotedString(str):
    """An object to differentiate from unquoted strings."""

    __slots__ = ()


class UnquotedString(str):
    """See https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#unquoted-strings."""

    __slots__ = ()

    def is_empty(self) -> bool:
        """Is given value an UnquotedString containing nothing or WHITE_CHARS only."""
        return not self.strip(WHITE_CHARS)
