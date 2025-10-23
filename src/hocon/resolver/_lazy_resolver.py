from copy import deepcopy
from dataclasses import dataclass
from functools import reduce, singledispatch
from typing import Callable, Type, get_args, Any

from hocon.constants import ANY_VALUE_TYPE, UNDEFINED, SIMPLE_VALUE_TYPE
from hocon.exceptions import HOCONConcatenationError
from hocon.resolver._simple_value import resolve_simple_value
from hocon.unresolved import UnresolvedConcatenation, UnresolvedDuplication, UnresolvedSubstitution, ANY_UNRESOLVED


@singledispatch
def resolve(values: Any) -> Any:
    raise NotImplementedError(f"Bad input value type: {type(values)}")


@resolve.register
def _(values: SIMPLE_VALUE_TYPE | UnresolvedSubstitution) -> SIMPLE_VALUE_TYPE | UnresolvedSubstitution:
    return values


@resolve.register
def _(values: list) -> list[Any]:
    resolved_list = []
    for element in values:
        resolved_elem = resolve(element)
        if resolved_elem is not UNDEFINED:
            resolved_list.append(resolved_elem)
    return resolved_list


@resolve.register
def _(values: dict) -> dict[Any, Any]:
    resolved_dict = {}
    for key, value in values.items():
        resolved_value = resolve(value)
        if resolved_value is not UNDEFINED:
            resolved_dict[key] = resolved_value
    return resolved_dict


@resolve.register
def _(values: UnresolvedConcatenation) -> ANY_VALUE_TYPE | UnresolvedConcatenation:
    values = values.sanitize()
    if not values:
        return UNDEFINED
    if len(values) == 1 and type(values[0]) in get_args(SIMPLE_VALUE_TYPE) + (UnresolvedSubstitution,):
        return values[0]
    concatenate_function = _get_concatenator(values)
    return concatenate_function(values)


@resolve.register
def _(values: UnresolvedDuplication) -> ANY_VALUE_TYPE | UnresolvedDuplication:
    """Resolve duplication values starting from the last (latest overrides/merges with the rest).
    If it's a SIMPLE_VALUE_TYPE or a list, it overrides the rest.
    If it's a dict type, objects will merge.
    If at any point of object merging, duplicate value is not a dict, merging will stop.
    """
    values = values.sanitize()
    last_value = resolve(values[-1])
    deduplicated = UnresolvedDuplication([last_value])
    if not isinstance(last_value, (dict, ANY_UNRESOLVED)):
        return last_value
    for value in reversed(values[:-1]):
        value = resolve(value)
        if isinstance(value, ANY_UNRESOLVED) or isinstance(deduplicated[0], ANY_UNRESOLVED):
            deduplicated.insert(0, value)
        elif isinstance(value, dict):
            if isinstance(deduplicated[0], dict):
                deduplicated[0] = merge(deduplicated[0], value)
            else:
                deduplicated.insert(0, value)
        else:
            break
    if len(deduplicated) == 1:
        return deduplicated[0]
    return deduplicated


def _get_concatenator(values: UnresolvedConcatenation) -> Callable[[UnresolvedConcatenation], ANY_VALUE_TYPE]:
    @dataclass(frozen=True)
    class ConcatenationType:
        type: Type[list | dict | str]
        has_substitutions: bool

    concat_type = ConcatenationType(type=values.get_type(), has_substitutions=values.has_substitutions())
    concatenate_functions: dict[ConcatenationType, Callable[[UnresolvedConcatenation], ANY_VALUE_TYPE]] = {
        ConcatenationType(list, True): _concatenate_lists_with_subs,
        ConcatenationType(dict, True): _concatenate_dicts_with_subs,
        ConcatenationType(str, True): _concatenate_simple_values_with_subs,
        ConcatenationType(list, False): _concatenate_lists,
        ConcatenationType(dict, False): _concatenate_dicts,
        ConcatenationType(str, False): _concatenate_simple_values,
    }
    return concatenate_functions.get(concat_type)


def _concatenate_dicts_with_subs(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    return reduce(merge_dict_concatenation, reversed(values))


def _concatenate_dicts(values: UnresolvedConcatenation) -> dict:
    return resolve(reduce(merge, reversed(values)))


def _concatenate_simple_values_with_subs(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    """[${a}, b, c, ${d}, e, f, g] should turn to [${a}, bc, ${d}, efg]"""
    result = UnresolvedConcatenation()
    chunks_to_concatenate: list[str] = []
    for value in values:
        if isinstance(value, UnresolvedSubstitution):
            if chunks_to_concatenate:
                if len(chunks_to_concatenate) == 1:
                    result.append(chunks_to_concatenate[0])
                else:
                    result.append(
                        _concatenate_simple_values(
                            UnresolvedConcatenation(chunks_to_concatenate), strip_left=False, strip_right=False
                        )
                    )
                chunks_to_concatenate = []
            result.append(value)
            continue
        chunks_to_concatenate.append(value)
    if chunks_to_concatenate:
        if len(chunks_to_concatenate) == 1:
            result.append(chunks_to_concatenate[0])
        else:
            result.append(_concatenate_simple_values(UnresolvedConcatenation(chunks_to_concatenate), strip_left=False))
    return result


def _concatenate_simple_values(
    values: UnresolvedConcatenation, strip_left: bool = True, strip_right: bool = True
) -> str:
    if not all(isinstance(value, str) for value in values):
        types = set([type(value).__name__ for value in values])
        raise HOCONConcatenationError(f"Lazy concatenation of types {types} not allowed.")
    return resolve_simple_value(values, strip_left=strip_left, strip_right=strip_right)


def _concatenate_lists_with_subs(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    result = UnresolvedConcatenation()
    chunks_to_concatenate: list[list] = []
    for value in values:
        if isinstance(value, UnresolvedSubstitution):
            if chunks_to_concatenate:
                result.append(_concatenate_lists(UnresolvedConcatenation(chunks_to_concatenate)))
                chunks_to_concatenate = []
            result.append(value)
            continue
        chunks_to_concatenate.append(value)
    if chunks_to_concatenate:
        result.append(_concatenate_lists(UnresolvedConcatenation(chunks_to_concatenate)))
    return result


def _concatenate_lists(values: UnresolvedConcatenation) -> list:
    if not all([isinstance(value, list) for value in values]):
        raise HOCONConcatenationError("Something went horribly wrong. This is a bug.")
    resolved_lists = []
    for value in values:
        resolved_lists.append(resolve(value))
    return sum(resolved_lists, [])


@singledispatch
def merge_dict_concatenation(superior, inferior: dict | UnresolvedSubstitution) -> dict | UnresolvedConcatenation:
    raise NotImplementedError(f"Bad input value type: {type(superior)}")


@merge_dict_concatenation.register(UnresolvedSubstitution)
def _(superior: UnresolvedSubstitution, inferior: dict | UnresolvedSubstitution) -> UnresolvedConcatenation:
    return UnresolvedConcatenation([inferior, superior])


@merge_dict_concatenation.register(dict)
def _(superior: dict, inferior: dict | UnresolvedSubstitution) -> dict | UnresolvedConcatenation:
    if isinstance(inferior, dict):
        return merge(superior, inferior)
    return UnresolvedConcatenation([inferior, superior])


@merge_dict_concatenation.register(UnresolvedConcatenation)
def _(superior: UnresolvedConcatenation, inferior: dict | UnresolvedSubstitution) -> dict | UnresolvedConcatenation:
    if isinstance(superior[0], dict) and isinstance(inferior, dict):
        superior[0] = merge(superior[0], inferior)
    else:
        superior.insert(0, inferior)
    return superior


def merge(superior: dict, inferior: dict) -> dict | UnresolvedConcatenation:
    """If both values are objects, then the objects are merged.
    If keys overlap, the latter wins."""
    result = deepcopy(inferior)
    for key, value in superior.items():
        inferior_value = result.get(key)
        if isinstance(inferior_value, ANY_UNRESOLVED):
            inferior_value = resolve(inferior_value)
        if isinstance(value, dict) and isinstance(inferior_value, dict):
            result[key] = merge(value, inferior_value)
        else:
            resolved_value = resolve(value)
            if resolved_value is not UNDEFINED:
                result[key] = resolved_value
    return result
