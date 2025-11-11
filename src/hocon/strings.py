from hocon.constants import WHITE_CHARS


class QuotedString(str):

    __slots__ = ()


class UnquotedString(str):

    __slots__ = ()

    def __repr__(self) -> str:
        return self.__str__()

    def is_empty(self) -> bool:
        """Is given value an UnquotedString containing nothing or WHITE_CHARS only."""
        return not self.strip(WHITE_CHARS)
