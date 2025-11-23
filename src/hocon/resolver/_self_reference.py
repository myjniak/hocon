from copy import deepcopy

from hocon.constants import ROOT_TYPE
from hocon.exceptions import HOCONSubstitutionUndefinedError
from hocon.unresolved import (
    UnresolvedConcatenation,
    UnresolvedDuplication,
    UnresolvedSubstitution,
)

__all__ = ["cut_self_reference_and_fields_that_override_it"]


class _Cutter:
    def __init__(self, sub: UnresolvedSubstitution) -> None:
        self.is_sub_found: bool = False
        self.sub = sub

    def cut(self, subtree: ROOT_TYPE, keypath_index: int = 0) -> None:
        is_past_last_key = keypath_index == len(self.sub.location)
        if is_past_last_key:
            return self.final_cut(subtree, keypath_index=keypath_index)
        key = self.sub.location[keypath_index]
        is_last_key = keypath_index + 1 == len(self.sub.location)
        if isinstance(subtree, (UnresolvedDuplication, UnresolvedConcatenation)):
            for item in subtree:
                self.cut(item, keypath_index)
        elif type(subtree) is dict and key in subtree:
            return self.cut_dict(subtree, key, keypath_index, is_last_key)
        elif type(subtree) is list and key.isdigit():
            return self.cut_list(subtree, key, keypath_index, is_last_key)
        return None

    def cut_list(self, subtree, key, keypath_index: int, is_last_key: bool):
        if not is_last_key:
            return self.cut(subtree[int(key)], keypath_index + 1)
        if subtree[int(key)] == self.sub or self.is_sub_found:
            self.is_sub_found = True
            del subtree[int(key)]
            return None
        self.cut(subtree[int(key)], keypath_index + 1)
        if not subtree[int(key)]:
            del subtree[int(key)]
        return None

    def cut_dict(self, subtree, key, keypath_index: int, is_last_key: bool):
        if not is_last_key:
            return self.cut(subtree[key], keypath_index + 1)
        if subtree[key] == self.sub or self.is_sub_found:
            subtree.pop(key)
            self.is_sub_found = True
            return None
        self.cut(subtree[key], keypath_index + 1)
        if not subtree[key]:
            subtree.pop(key)
        return None

    def final_cut(self, subtree, keypath_index: int = 0):
        if isinstance(subtree, UnresolvedDuplication):
            return self.cut_duplication(subtree, keypath_index=keypath_index)
        if isinstance(subtree, UnresolvedConcatenation):
            return self.cut_concatenation(subtree)
        raise HOCONSubstitutionUndefinedError(subtree)

    def cut_duplication(self, subtree, keypath_index: int = 0) -> None:
        for index, item in enumerate(subtree):
            if isinstance(item, UnresolvedConcatenation):
                self.cut(item, keypath_index)
            elif item == self.sub or self.is_sub_found:
                self.is_sub_found = True
                for _ in range(len(subtree) - index):
                    subtree.pop()
        index = len(subtree) - 1
        while index > 0:
            if not subtree[index]:
                subtree.pop(index)
            index -= 1

    def cut_concatenation(self, subtree) -> None:
        for index, item in enumerate(subtree):
            if item == self.sub or self.is_sub_found:
                self.is_sub_found = True
                for _ in range(len(subtree) - index):
                    subtree.pop()
                return


def cut_self_reference_and_fields_that_override_it(
    substitution: UnresolvedSubstitution,
    parsed: ROOT_TYPE,
) -> ROOT_TYPE:
    carved_parsed = deepcopy(parsed)
    cutter = _Cutter(substitution)
    cutter.cut(carved_parsed)
    return carved_parsed
