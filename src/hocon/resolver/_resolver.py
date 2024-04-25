from functools import reduce
from typing import Union, Callable, Any

from hocon.constants import ANY_VALUE_TYPE, WHITE_CHARS, SIMPLE_VALUE_TYPE, ROOT_TYPE, PreresolvedDuplicateValue, \
    UnresolvedDictConcatenation
from hocon.exceptions import HOCONConcatenationError, HOCONDuplicateKeyMergeError
from hocon.resolver._simple_value import resolve_simple_value
from hocon.strings import UnquotedString
from hocon.unresolved import UnresolvedConcatenation, UnresolvedDuplicateValue, UnresolvedSubstitution


def resolver_map() -> dict[str, Callable[[Any, ROOT_TYPE], Any]]:
    return {
        "dict": _resolve_dict,
        "list": _resolve_list,
        "UnresolvedConcatenation": concatenate,
        "UnresolvedDuplicateValue": deduplicate,
        "UnresolvedSubstitution": _resolve_substitution
    }


def resolve(parsed: ROOT_TYPE) -> ROOT_TYPE:
    if isinstance(parsed, list):
        return _resolve_list(parsed, parsed)
    else:
        return _resolve_dict(parsed, parsed)


def _resolve_value(value: ANY_VALUE_TYPE, parsed: ROOT_TYPE) -> ANY_VALUE_TYPE:
    func = resolver_map().get(type(value).__name__, lambda x, _: x)
    return func(value, parsed)


def _resolve_list(values: list, parsed: ROOT_TYPE) -> list:
    resolved_list = []
    for element in values:
        func = resolver_map().get(type(element).__name__, lambda x, _: x)
        resolved_list.append(func(element, parsed))
    return resolved_list


def _resolve_dict(dictionary: dict, parsed: ROOT_TYPE) -> dict:
    resolved_dict = {}
    for key, value in dictionary.items():
        func = resolver_map().get(type(value).__name__, lambda x, _: x)
        resolved_dict[key] = func(value, parsed)
    return resolved_dict


def concatenate(values: UnresolvedConcatenation, parsed: ROOT_TYPE) -> ANY_VALUE_TYPE:
    values = resolve_substitutions(values, parsed)
    if all(isinstance(value, dict) for value in values):
        resolved_dicts = [_resolve_dict(value, parsed) for value in values]
        return reduce(merge, resolved_dicts)
    if all(isinstance(value, str) for value in values):
        return resolve_simple_value(values)
    raise HOCONConcatenationError("Concatenation of multiple data types not allowed")


def deduplicate(values: UnresolvedDuplicateValue, parsed: ROOT_TYPE) -> ANY_VALUE_TYPE:
    if not all(isinstance(value, dict) for value in values):
        raise HOCONDuplicateKeyMergeError("Unresolved duplicate value not preresolved. Expected dicts only.")
    deduplicated = _resolve_value(values[-1], parsed)
    for value in reversed(values[:-1]):
        resolved_value = _resolve_value(value, parsed)
        deduplicated = merge(resolved_value, deduplicated)
    return deduplicated


def filter_out_unquoted_space(values: list[ANY_VALUE_TYPE]) -> list[ANY_VALUE_TYPE]:
    return list(filter(lambda value: not isinstance(value, UnquotedString) or value.strip(WHITE_CHARS), values))


def resolve_substitutions(values: UnresolvedConcatenation, parsed: ROOT_TYPE) -> UnresolvedConcatenation:
    values_with_resolved_substitutions = UnresolvedConcatenation()
    for value in values:
        if isinstance(value, UnresolvedSubstitution):
            values_with_resolved_substitutions.append(_resolve_substitution(value, parsed))
        else:
            values_with_resolved_substitutions.append(value)
    return values_with_resolved_substitutions


def _resolve_substitution(value: UnresolvedSubstitution, parsed: ROOT_TYPE) -> ANY_VALUE_TYPE:
    to_consider: list = []
    first_key = value.keys[0]
    if isinstance(parsed, list) and first_key.isdigit():
        subvalue = parsed[int(first_key)]
    elif isinstance(parsed, dict) and first_key in parsed:
        subvalue = parsed[first_key]
    else:
        subvalue = get_from_env(value)
    for key in value.keys[1:]:
        if isinstance(subvalue, UnresolvedDuplicateValue):
            # subvalue: UnresolvedDuplicateValue[UnresolvedDictConcatenation | dict]
            for value in subvalue:
                if isinstance(value, dict) and key in value:
                    subvalue = value[key]
        elif isinstance(subvalue, list) and key.isdigit():
            subvalue = subvalue[int(key)]
        elif isinstance(subvalue, dict) and key in subvalue:
            subvalue = subvalue[key]
        else:
            get_from_env(value)
    return subvalue


def get_from_env(value: UnresolvedSubstitution) -> str:
    return "from env"


def merge(dictionary: dict, superior_dict: dict[str, ANY_VALUE_TYPE]) -> dict:
    """If both values are objects, then the objects are merged.
    If keys overlap, the latter wins."""
    for key, value in superior_dict.items():
        if isinstance(value, dict) and isinstance(dictionary.get(key), dict):
            dictionary[key] = merge(dictionary[key], value)
        else:
            dictionary[key] = value
    return dictionary

#
#
#     def concatenate(self, values: UnresolvedConcatenation) -> ANY_VALUE_TYPE:
#         if not values:
#             raise HOCONConcatenationError("Unresolved concatenation cannot be empty")
#         # values = self.resolve_substitutions(values)
#         if any(isinstance(value, (UnresolvedConcatenation, UnresolvedDuplicateValue)) for value in values):
#             raise HOCONConcatenationError("Something went horribly wrong. This is a bug.")
#         if all(isinstance(value, str) for value in values):
#             return resolve_simple_value(values)
#         if any(isinstance(value, list) for value in values):
#             values = filter_out_unquoted_space(values)
#             if not all(isinstance(value, list) for value in values):
#                 raise HOCONConcatenationError(f"Arrays (lists) mixed with other value types not allowed")
#             resolved_lists = [self._resolve_list(value) for value in values]
#             return sum(resolved_lists, [])
#         if any(isinstance(value, dict) for value in values):
#             values = filter_out_unquoted_space(values)
#             if not all(isinstance(value, dict) for value in values):
#                 raise HOCONConcatenationError(f"Objects (dictionaries) mixed with other value types not allowed")
#             resolved_dicts = [self._resolve_dict(value) for value in values]
#             return reduce(merge, resolved_dicts)
#         if len(values) == 1:
#             return values[0]
#         raise HOCONConcatenationError("Concatenation of multiple data types not allowed")
#

#
#
# def filter_out_unquoted_space(values: list[ANY_VALUE_TYPE]) -> list[ANY_VALUE_TYPE]:
#     return list(filter(lambda value: not isinstance(value, UnquotedString) or value.strip(WHITE_CHARS), values))
#
#

#
#
