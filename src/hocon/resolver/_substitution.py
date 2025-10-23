from dataclasses import dataclass
from enum import Enum, auto
from typing import Self

from hocon.constants import ANY_VALUE_TYPE


class SubstitutionStatus(Enum):
    UNRESOLVED = auto()
    RESOLVING = auto()
    FALLBACK_UNRESOLVED = auto()
    FALLBACK_RESOLVING = auto()
    RESOLVED = auto()
    UNDEFINED = auto()

    def to_resolving(self) -> Self | None:
        state_change_map = {
            SubstitutionStatus.UNRESOLVED: SubstitutionStatus.RESOLVING,
            SubstitutionStatus.FALLBACK_UNRESOLVED: SubstitutionStatus.FALLBACK_RESOLVING,
        }
        return state_change_map.get(self)

    @property
    def is_resolved(self) -> bool:
        return self == SubstitutionStatus.RESOLVED


@dataclass
class Substitution:
    value: ANY_VALUE_TYPE = None
    status: SubstitutionStatus = SubstitutionStatus.UNRESOLVED
