from dataclasses import dataclass


class UnresolvedConcatenation(list):
    def __repr__(self):
        list_str = super().__repr__()
        return "\n〈" + list_str[1:-1].replace("\n", "\n    ") + "〉\n"


class UnresolvedDuplicateValue(list):
    def __repr__(self):
        list_str = super().__repr__()
        return "\n【\n" + list_str[1:-1].replace("\n", "\n    ") + "\n】\n"


@dataclass
class UnresolvedSubstitution:
    keys: list[str]
    optional: bool

    def __str__(self):
        return r"${" + ("?" if self.optional else "") + ".".join(self.keys) + r"}"

    def __repr__(self):
        return self.__str__()
