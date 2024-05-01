"""Utils for dictionary value / list element evaluation."""
from copy import deepcopy
from functools import reduce

from ..constants import ANY_VALUE_TYPE
from ..unresolved import UnresolvedConcatenation, UnresolvedDuplicateValue


def merge_unconcatenated(unconcatenated_dictionary: dict, keys: list, unconcatenated_value: UnresolvedConcatenation):
    def set_default(dictionary: dict, key: str) -> dict:
        value = dictionary.get(key)
        new_element: dict = {}
        if isinstance(value, UnresolvedDuplicateValue):
            value.append(new_element)
        elif value is not None:
            dictionary[key] = UnresolvedDuplicateValue((value, new_element))
        else:
            dictionary[key] = new_element
        return new_element

    last_nest = reduce(set_default, keys[:-1], unconcatenated_dictionary)
    if isinstance(last_nest.get(keys[-1]), UnresolvedDuplicateValue):
        last_nest[keys[-1]].append(unconcatenated_value)
    elif last_nest.get(keys[-1]) is not None:
        last_nest[keys[-1]] = UnresolvedDuplicateValue((last_nest[keys[-1]], unconcatenated_value))
    else:
        last_nest[keys[-1]] = unconcatenated_value
    return deepcopy(unconcatenated_dictionary)
