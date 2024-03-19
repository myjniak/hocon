"""Utils for dictionary value / list element evaluation."""
from copy import deepcopy
from functools import reduce

from hocon.constants import ANY_VALUE_TYPE
from hocon.unresolved import UnresolvedConcatenation, UnresolvedDuplicateValue


def merge_unconcatenated(unconcatenated_dictionary: dict, keys: list, unconcatenated_value: UnresolvedConcatenation):
    def set_default(dictionary: dict, key: str):
        value = dictionary.get(key)
        if isinstance(value, UnresolvedDuplicateValue):
            new_element = {}
            value.append(new_element)
            return new_element
        if value is not None:
            new_element = {}
            dictionary[key] = UnresolvedDuplicateValue((value, new_element))
            return new_element
        dictionary[key] = {}
        return dictionary[key]

    last_nest = reduce(set_default, keys[:-1], unconcatenated_dictionary)
    if isinstance(last_nest.get(keys[-1]), UnresolvedDuplicateValue):
        last_nest[keys[-1]].append(unconcatenated_value)
    elif last_nest.get(keys[-1]) is not None:
        last_nest[keys[-1]] = UnresolvedDuplicateValue((last_nest[keys[-1]], unconcatenated_value))
    else:
        last_nest[keys[-1]] = unconcatenated_value
    return deepcopy(unconcatenated_dictionary)


def evaluate_path_value(keys: list[str], value: list[ANY_VALUE_TYPE]) -> ANY_VALUE_TYPE:
    if len(keys) == 1:
        return value
    dictionary = {keys[-1]: value}
    for key in reversed(keys[1:-1]):
        dictionary = {key: dictionary}
    return dictionary
