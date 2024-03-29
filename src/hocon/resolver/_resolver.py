from functools import reduce
from typing import Union

from hocon.constants import ANY_VALUE_TYPE, WHITE_CHARS
from hocon.exceptions import HOCONConcatenationError, HOCONDuplicateKeyMergeError
from hocon.resolver._simple_value import resolve_simple_value
from hocon.strings import UnquotedString
from hocon.unresolved import UnresolvedConcatenation, UnresolvedDuplicateValue


def resolve(parsed: Union[list, dict]) -> Union[list, dict]:
    if isinstance(parsed, list):
        return _resolve_list(parsed)
    else:
        return _resolve_dict(parsed)


def _resolve_value(value: ANY_VALUE_TYPE) -> ANY_VALUE_TYPE:
    resolve_func = {
        "dict": _resolve_dict,
        "list": _resolve_list,
        "UnresolvedConcatenation": concatenate,
        "UnresolvedDuplicateValue": deduplicate
    }
    func = resolve_func.get(type(value).__name__, lambda x: x)
    return func(value)


def _resolve_list(parsed: list) -> list:
    resolved_list = []
    resolve_func = {
        "dict": _resolve_dict,
        "list": _resolve_list,
        "UnresolvedConcatenation": concatenate,
        "UnresolvedDuplicateValue": deduplicate
    }
    for element in parsed:
        func = resolve_func.get(type(element).__name__, lambda x: x)
        resolved_list.append(func(element))
    return resolved_list


def _resolve_dict(parsed: dict) -> dict:
    resolved_dict = {}
    resolve_func = {
        "dict": _resolve_dict,
        "list": _resolve_list,
        "UnresolvedConcatenation": concatenate,
        "UnresolvedDuplicateValue": deduplicate
    }
    for key, value in parsed.items():
        func = resolve_func.get(type(value).__name__, lambda x: x)
        resolved_dict[key] = func(value)
    return resolved_dict


def concatenate(values: UnresolvedConcatenation) -> ANY_VALUE_TYPE:
    if not values:
        raise HOCONConcatenationError("Unresolved concatenation cannot be empty")
    if any(isinstance(value, (UnresolvedConcatenation, UnresolvedDuplicateValue)) for value in values):
        raise HOCONConcatenationError("Something went horribly wrong. This is a bug.")
    if all(isinstance(value, str) for value in values):
        return resolve_simple_value(values)
    if any(isinstance(value, list) for value in values):
        values = filter_out_unquoted_space(values)
        if not all(isinstance(value, list) for value in values):
            raise HOCONConcatenationError(f"Arrays (lists) mixed with other value types not allowed")
        resolved_lists = [_resolve_list(value) for value in values]
        return sum(resolved_lists, [])
    if any(isinstance(value, dict) for value in values):
        values = filter_out_unquoted_space(values)
        if not all(isinstance(value, dict) for value in values):
            raise HOCONConcatenationError(f"Objects (dictionaries) mixed with other value types not allowed")
        resolved_dicts = [_resolve_dict(value) for value in values]
        return reduce(merge, resolved_dicts)
    if len(values) == 1:
        return values[0]
    raise HOCONConcatenationError("Multiple types concatenation not allowed")


def filter_out_unquoted_space(values: list[ANY_VALUE_TYPE]) -> list[ANY_VALUE_TYPE]:
    return list(filter(lambda value: not isinstance(value, UnquotedString) or value.strip(WHITE_CHARS), values))


def deduplicate(values: UnresolvedDuplicateValue) -> ANY_VALUE_TYPE:
    if not values:
        raise HOCONDuplicateKeyMergeError("Unresolved duplicate key must contain at least 2 elements.")
    deduplicated = _resolve_value(values[-1])
    for value in reversed(values[:-1]):
        resolved_value = _resolve_value(value)
        if isinstance(deduplicated, dict) and isinstance(resolved_value, dict):
            deduplicated = merge(resolved_value, deduplicated)
        else:
            break
    return deduplicated


def merge(dictionary: dict, superior_dict: dict[str, ANY_VALUE_TYPE]) -> dict:
    """If both values are objects, then the objects are merged.
    If keys overlap, the latter wins."""
    for key, value in superior_dict.items():
        if isinstance(value, dict) and isinstance(dictionary.get(key), dict):
            dictionary[key] = merge(dictionary[key], value)
        else:
            dictionary[key] = value
    return dictionary
