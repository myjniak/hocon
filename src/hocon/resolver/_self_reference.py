from copy import deepcopy

from ..constants import ROOT_TYPE
from ..exceptions import HOCONSubstitutionUndefinedError
from ..unresolved import UnresolvedConcatenation, UnresolvedSubstitution, UnresolvedDuplication


class Cutter:
    def __init__(self, sub: UnresolvedSubstitution):
        self.is_sub_found: bool = False
        self.sub = sub

    def cut(self, subtree: ROOT_TYPE, keypath_index: int = 0) -> None:
        is_past_last_key = keypath_index == len(self.sub.location)
        if is_past_last_key:
            if isinstance(subtree, UnresolvedDuplication):
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
                return
            elif isinstance(subtree, UnresolvedConcatenation):
                for index, item in enumerate(subtree):
                    if item == self.sub or self.is_sub_found:
                        self.is_sub_found = True
                        for _ in range(len(subtree) - index):
                            subtree.pop()
                        return
                return
            raise HOCONSubstitutionUndefinedError(subtree)
        key = self.sub.location[keypath_index]
        is_last_key = keypath_index + 1 == len(self.sub.location)
        if isinstance(subtree, (UnresolvedDuplication, UnresolvedConcatenation)):
            for item in subtree:
                self.cut(item, keypath_index)
        if not is_last_key:
            if type(subtree) is dict and key in subtree:
                self.cut(subtree[key], keypath_index + 1)
            elif type(subtree) is list and key.isdigit():
                self.cut(subtree[int(key)], keypath_index + 1)
            else:
                raise HOCONSubstitutionUndefinedError(f"Something went horribly wrong. This is a bug.")
        else:
            if type(subtree) is dict and key in subtree:
                if subtree[key] == self.sub or self.is_sub_found:
                    subtree.pop(key)
                    self.is_sub_found = True
                    return
                else:
                    self.cut(subtree[key], keypath_index + 1)
                    if not subtree[key]:
                        subtree.pop(key)
            elif type(subtree) is list and key.isdigit():
                if subtree[int(key)] == self.sub or self.is_sub_found:
                    self.is_sub_found = True
                    del subtree[int(key)]
                    return
                else:
                    self.cut(subtree[int(key)], keypath_index + 1)
                    if not subtree[int(key)]:
                        del subtree[int(key)]


def cut_self_reference_and_fields_that_override_it(
    substitution: UnresolvedSubstitution, parsed: ROOT_TYPE
) -> ROOT_TYPE:
    carved_parsed = deepcopy(parsed)
    cutter = Cutter(substitution)
    cutter.cut(carved_parsed)
    return carved_parsed
