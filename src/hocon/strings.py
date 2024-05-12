class QuotedString(str): ...


class UnquotedString(str):
    def __repr__(self):
        return self.__str__()
