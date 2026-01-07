from typing import overload

from hocon.unresolved import (
    UnresolvedConcatenation,
    UnresolvedSubstitution,
)

@overload
def merge_dict_concatenation(
    superior: UnresolvedSubstitution,
    inferior: dict | UnresolvedSubstitution,
) -> UnresolvedConcatenation: ...
@overload
def merge_dict_concatenation(
    superior: dict,
    inferior: dict | UnresolvedSubstitution,
) -> dict | UnresolvedConcatenation: ...
@overload
def merge_dict_concatenation(
    superior: UnresolvedConcatenation,
    inferior: dict | UnresolvedSubstitution,
) -> dict | UnresolvedConcatenation: ...
