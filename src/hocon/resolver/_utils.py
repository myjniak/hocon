import os
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Optional

from ..constants import WHITE_CHARS, ROOT_TYPE, ANY_VALUE_TYPE, UNDEFINED
from ..exceptions import HOCONConcatenationError, HOCONSubstitutionUndefinedError
from ..strings import UnquotedString, QuotedString
from ..unresolved import UnresolvedConcatenation, UnresolvedSubstitution, UnresolvedDuplicateValue


class SubstitutionStatus(Enum):
    UNRESOLVED = auto()
    RESOLVING = auto()
    FALLBACK_UNRESOLVED = auto()
    FALLBACK_RESOLVING = auto()
    RESOLVED = auto()
    UNDEFINED = auto()


@dataclass
class Substitution:
    value: ANY_VALUE_TYPE = None
    status: SubstitutionStatus = SubstitutionStatus.UNRESOLVED


def sanitize_unresolved_concatenation(concatenation: UnresolvedConcatenation) -> UnresolvedConcatenation:
    concatenation = filter_out_undefined_substitutions(concatenation)
    if any(isinstance(value, list) for value in concatenation):
        concatenation = filter_out_unquoted_space(concatenation)
        if not all(isinstance(value, list | UnresolvedSubstitution) for value in concatenation):
            raise HOCONConcatenationError(f"Arrays (lists) mixed with other value types not allowed")
    if any(isinstance(value, dict) for value in concatenation):
        concatenation = filter_out_unquoted_space(concatenation)
        if not all(isinstance(value, dict | UnresolvedSubstitution) for value in concatenation):
            raise HOCONConcatenationError(f"Objects (dictionaries) mixed with other value types not allowed")
    if any(isinstance(value, str) for value in concatenation):
        concatenation = strip_unquoted_space(concatenation)
    return concatenation


def filter_out_undefined_substitutions(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    return UnresolvedConcatenation(filter(lambda v: v is not UNDEFINED, values))


def filter_out_unquoted_space(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    def is_relevant(element) -> bool:
        if isinstance(element, UnquotedString) and not element.strip(WHITE_CHARS):
            return False
        return True

    return UnresolvedConcatenation(filter(is_relevant, values))


def strip_unquoted_space(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    def is_unquoted_string_with_space_only(value: Any) -> bool:
        return isinstance(value, UnquotedString) and not value.strip(WHITE_CHARS)

    try:
        first = next(index for index, value in enumerate(values) if not is_unquoted_string_with_space_only(value))
    except StopIteration:
        return UnresolvedConcatenation([])
    last = -1 * next(
        index for index, value in enumerate(reversed(values)) if not is_unquoted_string_with_space_only(value)
    )
    if last == 0:
        return UnresolvedConcatenation(values[first:])
    return UnresolvedConcatenation(values[first:last])


def get_from_env(substitution: UnresolvedSubstitution) -> Substitution:
    env_value: Optional[str] = os.getenv(".".join(substitution.keys))
    if env_value is None:
        return Substitution(value=UNDEFINED, status=SubstitutionStatus.UNDEFINED)
    return Substitution(value=QuotedString(env_value), status=SubstitutionStatus.RESOLVED)


def cut_self_reference_and_fields_that_override_it(
    substitution: UnresolvedSubstitution, parsed: ROOT_TYPE
) -> ROOT_TYPE:
    class Cutter:
        def __init__(self, sub: UnresolvedSubstitution):
            self.is_sub_found: bool = False
            self.sub = sub

        def cut(self, subtree: ROOT_TYPE, keypath_index: int = 0):
            key = self.sub.location[keypath_index]
            if isinstance(subtree, dict) and key in subtree:
                subtree_item = subtree[key]
            elif isinstance(subtree, list) and key.isdigit():
                subtree_item = subtree[int(key)]
            else:
                raise HOCONSubstitutionUndefinedError("Something went horribly wrong. This is a bug.")
            if isinstance(subtree_item, UnresolvedDuplicateValue):
                for index, item in enumerate(subtree_item):
                    assert isinstance(item, UnresolvedConcatenation)
                    self._scan_concatenation(item, keypath_index)
                    if self.is_sub_found:
                        for _ in range(len(subtree_item) - index):
                            subtree_item.pop()
                        break
            elif isinstance(subtree_item, UnresolvedConcatenation):
                self._scan_concatenation(subtree_item, keypath_index)
            if not subtree_item:
                subtree.pop(key)

        def _scan_concatenation(self, concatenation: UnresolvedConcatenation, keypath_index: int):
            for index, item in enumerate(concatenation):
                if isinstance(item, ROOT_TYPE) and keypath_index + 1 < len(self.sub.location):
                    self.cut(item, keypath_index=keypath_index + 1)
                if item == self.sub or self.is_sub_found:
                    self.is_sub_found = True
                    for _ in range(len(concatenation) - index):
                        concatenation.pop()
                    break

    carved_parsed = deepcopy(parsed)
    cutter = Cutter(substitution)
    cutter.cut(carved_parsed)
    return carved_parsed
