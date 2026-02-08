import operator
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from functools import cache, reduce, singledispatch
from typing import Any, get_args

from hocon.constants import ANY_VALUE_TYPE, SIMPLE_VALUE_TYPE, UNDEFINED, Undefined
from hocon.exceptions import HOCONConcatenationError
from hocon.resolver._simple_value import resolve_simple_value
from hocon.strings import HOCON_STRING
from hocon.unresolved import (
    ANY_UNRESOLVED,
    UnresolvedConcatenation,
    UnresolvedDuplication,
    UnresolvedSubstitution,
)


@singledispatch
def resolve(values: ANY_VALUE_TYPE | ANY_UNRESOLVED) -> Undefined | ANY_VALUE_TYPE | ANY_UNRESOLVED:
    msg = f"Bad input value type: {type(values)}"
    raise NotImplementedError(msg)


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
    return _resolve_dict(values)


@resolve.register
def _(values: UnresolvedConcatenation) -> Undefined | ANY_VALUE_TYPE | UnresolvedSubstitution | UnresolvedConcatenation:
    values = values.sanitize()
    if not values:
        return UNDEFINED
    first_value = values[0]
    if len(values) == 1 and (
        type(first_value) is str
        or type(first_value) is int
        or type(first_value) is bool
        or type(first_value) is None
        or type(first_value) is UnresolvedSubstitution
    ):
        return first_value
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
    if isinstance(last_value, SIMPLE_VALUE_TYPE) or type(last_value) is list:
        return last_value

    first_value = resolve(values[0])
    deduplicated = UnresolvedDuplication([first_value])
    for value in values[1:]:
        maybe_resolved_value = resolve(value)
        if isinstance(maybe_resolved_value, get_args(ANY_UNRESOLVED)) or isinstance(
            deduplicated[0],
            get_args(ANY_UNRESOLVED),
        ):
            deduplicated.append(maybe_resolved_value)
        elif isinstance(maybe_resolved_value, dict):
            if isinstance(deduplicated[-1], dict):
                deduplicated[-1] = merge(maybe_resolved_value, deduplicated[-1])
            else:
                deduplicated.append(maybe_resolved_value)
        else:
            deduplicated = UnresolvedDuplication([maybe_resolved_value])
    if len(deduplicated) == 1 and isinstance(deduplicated[0], ANY_VALUE_TYPE):
        return deduplicated[0]
    return deduplicated


def _resolve_dict(values: dict) -> dict[Any, Any]:
    resolved_dict = {}
    for key, value in values.items():
        resolved_value = resolve(value)
        if resolved_value is not UNDEFINED:
            resolved_dict[key] = resolved_value
    return resolved_dict


@dataclass(frozen=True)
class ConcatenationType:
    """With 3 types than can have subs, that makes 6 different methods of resolving concatenations."""

    type: type
    has_substitutions: bool


def _get_concatenator(
    values: UnresolvedConcatenation,
) -> Callable[
    [UnresolvedConcatenation],
    dict | list | SIMPLE_VALUE_TYPE | UnresolvedSubstitution | UnresolvedConcatenation,
]:
    concatenate_functions = _get_concatenators()
    concat_type = ConcatenationType(type=values.get_type(), has_substitutions=values.has_substitutions())
    return concatenate_functions[concat_type]


@cache
def _get_concatenators() -> dict[
    ConcatenationType,
    Callable[
        [UnresolvedConcatenation],
        dict | list | SIMPLE_VALUE_TYPE | UnresolvedSubstitution | UnresolvedConcatenation,
    ],
]:
    return {
        ConcatenationType(list, has_substitutions=True): _concatenate_lists_with_subs,
        ConcatenationType(dict, has_substitutions=True): _concatenate_dicts_with_subs,
        ConcatenationType(str, has_substitutions=True): _concatenate_simple_values_with_subs,
        ConcatenationType(list, has_substitutions=False): _concatenate_lists,
        ConcatenationType(dict, has_substitutions=False): _concatenate_dicts,
        ConcatenationType(str, has_substitutions=False): _concatenate_simple_values,
    }


def _concatenate_dicts_with_subs(
    values: list[dict | UnresolvedSubstitution | UnresolvedConcatenation],
) -> dict | UnresolvedConcatenation | UnresolvedSubstitution:
    return reduce(merge_dict_concatenation, reversed(values))


def _concatenate_dicts(values: list[dict]) -> dict:
    return _resolve_dict(reduce(merge, reversed(values)))


def _concatenate_simple_values_with_subs(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    """Turn [${a}, b, c, ${d}, e, f, g] into [${a}, bc, ${d}, efg]."""
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
                            UnresolvedConcatenation(chunks_to_concatenate),
                            strip_left=False,
                            strip_right=False,
                        ),
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
    values: UnresolvedConcatenation,
    *,
    strip_left: bool = True,
    strip_right: bool = True,
) -> SIMPLE_VALUE_TYPE:
    if not all(isinstance(value, HOCON_STRING) for value in values):
        types = {type(value).__name__ for value in values}
        msg = f"Lazy concatenation of types {types} not allowed."
        raise HOCONConcatenationError(msg)
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
    resolved_lists = [resolve(value) for value in values]
    return reduce(operator.iadd, resolved_lists, [])


@singledispatch
def merge_dict_concatenation(
    superior: dict | UnresolvedSubstitution | UnresolvedConcatenation,
    _: dict | UnresolvedSubstitution,
) -> dict | UnresolvedConcatenation:
    msg = f"Bad input value type: {type(superior)}"
    raise NotImplementedError(msg)


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


def merge(superior: dict, inferior: dict) -> dict:
    """Merge two objects recursively. If keys overlap, the latter wins."""
    result = deepcopy(inferior)
    for key, value in superior.items():
        inferior_value = result.get(key)
        if isinstance(inferior_value, get_args(ANY_UNRESOLVED)):
            inferior_value = resolve(inferior_value)
        if isinstance(value, dict) and isinstance(inferior_value, dict):
            result[key] = merge(value, inferior_value)
        else:
            resolved_value = resolve(value)
            if resolved_value is not UNDEFINED:
                result[key] = resolved_value
    return result
