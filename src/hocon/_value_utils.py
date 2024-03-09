"""Utils for dictionary value / list element evaluation."""
from functools import reduce

from .constants import ANY_VALUE_TYPE
from .exceptions import HOCONDecodeError


def concatenate(values: list[ANY_VALUE_TYPE]) -> ANY_VALUE_TYPE:
    if not values:
        raise HOCONDecodeError("Expected value not found")
    if all(isinstance(value, list) for value in values):
        return sum(values, [])
    if all(isinstance(value, dict) for value in values):
        return reduce(merge, values)
    if all(isinstance(value, str) for value in values):
        return "".join(values)
    if len(values) == 1:
        return values[0]
    raise HOCONDecodeError("Multiple types concatenation not supported")


def merge(dictionary: dict, superior_dict: dict[str, ANY_VALUE_TYPE]) -> dict:
    """If both values are objects, then the objects are merged.
    If keys overlap, the latter wins."""
    for key, value in superior_dict.items():
        if isinstance(value, dict) and isinstance(dictionary.get(key), dict):
            dictionary[key] = merge(dictionary[key], value)
        else:
            dictionary[key] = value
    return dictionary


def evaluate_path_value(keys: list[str], value) -> ANY_VALUE_TYPE:
    if len(keys) == 1:
        return value
    dictionary = {keys[-1]: value}
    for key in reversed(keys[1:-1]):
        dictionary = {key: dictionary}
    return dictionary
