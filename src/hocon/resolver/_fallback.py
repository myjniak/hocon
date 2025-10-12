from copy import deepcopy

from ..constants import ROOT_TYPE
from ..exceptions import HOCONSubstitutionUndefinedError
from ..unresolved import UnresolvedConcatenation, UnresolvedSubstitution, UnresolvedDuplicateValue


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
            raise HOCONSubstitutionUndefinedError(f"Something went horribly wrong. This is a bug.")
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
            if item == self.sub:  # or self.is_sub_found:
                self.is_sub_found = True
                for _ in range(len(concatenation) - index):
                    concatenation.pop()
                break


def cut_self_reference_and_fields_that_override_it(
    substitution: UnresolvedSubstitution, parsed: ROOT_TYPE
) -> ROOT_TYPE:
    carved_parsed = deepcopy(parsed)
    cutter = Cutter(substitution)
    cutter.cut(carved_parsed)
    return carved_parsed
