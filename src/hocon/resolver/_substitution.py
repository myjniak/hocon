from dataclasses import dataclass
from enum import Enum, auto

from hocon.constants import ANY_VALUE_TYPE, Undefined


class SubstitutionStatus(Enum):
    """Starts always from UNRESOLVED. Ends on RESOLVED or UNDEFINED.

    State transitions documented for each state inline.
    """

    UNRESOLVED = auto(), "--> RESOLVING"
    RESOLVING = auto(), "--> RESOLVED, UNDEFINED, FALLBACK_UNRESOLVED"
    FALLBACK_UNRESOLVED = auto(), "--> FALLBACK_RESOLVING"
    FALLBACK_RESOLVING = auto(), "--> RESOLVED, UNDEFINED"
    RESOLVED = auto(), "happy end :)"
    UNDEFINED = auto(), "bad ending :("

    def to_resolving(self) -> "SubstitutionStatus | None":
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
    """Resolver's representation of a ${substitution}."""

    value: ANY_VALUE_TYPE | Undefined = None
    status: SubstitutionStatus = SubstitutionStatus.UNRESOLVED
