"""Hocon needs to distinguish "quoted" from unquoted strings."""

from collections import UserString

from hocon.constants import WHITE_CHARS


class QuotedString(UserString):
    """An object to differentiate from unquoted strings."""

    __slots__ = ()


class UnquotedString(UserString):
    """See https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#unquoted-strings."""

    __slots__ = ()

    def is_empty(self) -> bool:
        """Is given value an UnquotedString containing nothing or WHITE_CHARS only."""
        return not self.strip(WHITE_CHARS)


HOCON_STRING = QuotedString | UnquotedString | str
