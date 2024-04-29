from dataclasses import dataclass, field
from itertools import count
from enum import Enum, auto


class UnresolvedConcatenation(list):
    def __repr__(self):
        list_str = super().__repr__()
        return "\n〈" + list_str[1:-1].replace("\n", "\n    ") + "〉\n"


class UnresolvedDuplicateValue(list):
    def __repr__(self):
        list_str = super().__repr__()
        return "\n【\n" + list_str[1:-1].replace("\n", "\n    ") + "\n】\n"


class SubstitutionStatus(Enum):
    UNRESOLVED = auto()
    RESOLVING = auto()
    RESOLVED = auto()


@dataclass
class UnresolvedSubstitution:
    keys: list[str]
    optional: bool
    identifier: int = field(default_factory=count().__next__)
    status = SubstitutionStatus = SubstitutionStatus.UNRESOLVED
    value = None

    def __str__(self):
        return r"${" + ("?" if self.optional else "") + ".".join(self.keys) + r"}"

    def __repr__(self):
        return self.__str__()
