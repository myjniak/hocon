from dataclasses import dataclass, field
from itertools import count
from typing import Optional


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
    relative_location: Optional[list[str]] = None
    including_root: Optional[list[str]] = None
    identifier: int = field(default_factory=count().__next__)

    def __post_init__(self):
        if self.including_root is None:
            self.including_root = []

    @property
    def location(self):
        return self.including_root + self.relative_location

    def __str__(self):
        return r"${" + ("?" if self.optional else "") + ".".join(self.keys) + r"}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other: object):
        if not isinstance(other, UnresolvedSubstitution):
            return NotImplemented
        return self.keys == other.keys and self.optional == other.optional

    def __hash__(self):
        return hash((".".join(self.keys), self.optional, self.location, self.identifier))
