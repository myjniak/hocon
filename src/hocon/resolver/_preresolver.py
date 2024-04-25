from typing import Union, Callable, Any

from hocon.constants import ANY_VALUE_TYPE, WHITE_CHARS, SIMPLE_VALUE_TYPE, ROOT_TYPE, ANY_UNRESOLVED
from hocon.exceptions import HOCONConcatenationError, HOCONDuplicateKeyMergeError
from hocon.resolver._simple_value import resolve_simple_value
from hocon.strings import UnquotedString
from hocon.unresolved import UnresolvedConcatenation, UnresolvedDuplicateValue, UnresolvedSubstitution


def resolver_map() -> dict[str, Callable[[ANY_UNRESOLVED, ROOT_TYPE], ANY_UNRESOLVED]]:
    return {
        "dict": _resolve_dict,
        "list": _resolve_list,
        "UnresolvedConcatenation": concatenate,
        "UnresolvedDuplicateValue": deduplicate
    }


def preresolve(parsed: ROOT_TYPE) -> ROOT_TYPE:
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


def _preconcatenate(values: UnresolvedConcatenation) -> UnresolvedConcatenation | UnresolvedSubstitution:
    if len(values) == 1:
        return values[0]
    if all(isinstance(value, Union[str, UnresolvedSubstitution]) for value in values):
        return values
    raise HOCONConcatenationError("Sustitutions cannot be a part of list / dict concatenation.")


def concatenate(values: UnresolvedConcatenation, parsed: ROOT_TYPE) -> ANY_UNRESOLVED:
    if not values:
        raise HOCONConcatenationError("Unresolved concatenation cannot be empty")
    if any(isinstance(value, (UnresolvedConcatenation, UnresolvedDuplicateValue)) for value in values):
        raise HOCONConcatenationError("Something went horribly wrong. This is a bug.")
    if any(isinstance(value, UnresolvedSubstitution) for value in values):
        return _preconcatenate(values)
    if all(isinstance(value, str) for value in values):
        return resolve_simple_value(values)
    if any(isinstance(value, list) for value in values):
        values = filter_out_unquoted_space(values)
        if not all(isinstance(value, list) for value in values):
            raise HOCONConcatenationError(f"Arrays (lists) mixed with other value types not allowed")
        resolved_lists = [_resolve_list(value, parsed) for value in values]
        return sum(resolved_lists, [])
    if any(isinstance(value, dict) for value in values):
        values = filter_out_unquoted_space(values)
        if not all(isinstance(value, dict) for value in values):
            raise HOCONConcatenationError(f"Objects (dictionaries) mixed with other value types not allowed")
        resolved_dicts = UnresolvedConcatenation([_resolve_dict(value, parsed) for value in values])
        if len(resolved_dicts) == 1:
            return resolved_dicts[0]
        return resolved_dicts
    if len(values) == 1:
        return values[0]
    raise HOCONConcatenationError("Concatenation of multiple data types not allowed")


def deduplicate(values: UnresolvedDuplicateValue, parsed: ROOT_TYPE) -> ANY_VALUE_TYPE | UnresolvedDuplicateValue:
    if not values:
        raise HOCONDuplicateKeyMergeError("Unresolved duplicate key must contain at least 2 elements.")
    return_values = UnresolvedDuplicateValue()
    for value in reversed(values):
        resolved_value = _resolve_value(value, parsed)
        if isinstance(resolved_value, Union[dict, UnresolvedConcatenation]):
            return_values.append(resolved_value)
        elif isinstance(resolved_value, Union[SIMPLE_VALUE_TYPE, list]):
            if len(return_values) == 0:
                return resolved_value
            elif len(return_values) == 1:
                return return_values[0]
            return_values.reverse()
            return return_values
        else:
            raise HOCONDuplicateKeyMergeError(f"Unexpected data type: {type(resolved_value)}")
    return_values.reverse()
    return return_values


def filter_out_unquoted_space(values: list[ANY_VALUE_TYPE]) -> list[ANY_VALUE_TYPE]:
    return list(filter(lambda value: not isinstance(value, UnquotedString) or value.strip(WHITE_CHARS), values))
