import operator
from collections.abc import Callable
from copy import deepcopy
from dataclasses import dataclass
from functools import cache, reduce, singledispatch
from typing import Any

from hocon.constants import ANY_VALUE_TYPE, SIMPLE_VALUE_TYPE
from hocon.exceptions import HOCONConcatenationError
from hocon.unresolved import (
    ANY_UNRESOLVED,
    UnresolvedConcatenation,
    UnresolvedDuplication,
    UnresolvedSubstitution,
)


@singledispatch
def resolve(values: ANY_VALUE_TYPE | ANY_UNRESOLVED) -> ANY_VALUE_TYPE | ANY_UNRESOLVED:
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
        resolved_list.append(resolved_elem)
    return resolved_list


@resolve.register
def _(values: dict) -> dict[Any, Any]:
    return _resolve_dict(values)


@resolve.register
def _(values: UnresolvedConcatenation) -> ANY_VALUE_TYPE | UnresolvedSubstitution | UnresolvedConcatenation:
    concatenation = values.sanitize()
    if not concatenation:
        msg = f"Invalid empty concatenation provided! {values}"
        raise HOCONConcatenationError(msg)
    first_value = concatenation[0]
    if len(concatenation) == 1 and (
        type(first_value) is str
        or type(first_value) is int
        or type(first_value) is bool
        or type(first_value) is None
        or type(first_value) is UnresolvedSubstitution
    ):
        return first_value
    concatenate_function = _get_concatenator(concatenation)
    return concatenate_function(concatenation)


@resolve.register
def _(values: UnresolvedDuplication) -> ANY_VALUE_TYPE | UnresolvedDuplication:
    """Resolve duplication values starting from the first (each latter item overrides/merges with the previous item).

    If it's a SIMPLE_VALUE_TYPE or a list, it overrides the rest.
    If it's a dict type, objects will merge.
    If at any point of object merging, duplicate value is not a dict, merging will stop.
    """
    values = values.sanitize()
    first_value = resolve(values[0])
    deduplicated = UnresolvedDuplication([first_value])
    for value in values[1:]:
        maybe_resolved_value = resolve(value)
        if isinstance(maybe_resolved_value, dict) and isinstance(deduplicated[-1], dict):
            deduplicated[-1] = merge(maybe_resolved_value, deduplicated[-1])
        else:
            deduplicated.append(maybe_resolved_value)
    if len(deduplicated) == 1 and isinstance(deduplicated[0], ANY_VALUE_TYPE):
        return deduplicated[0]
    return deduplicated


def _resolve_dict(values: dict) -> dict[Any, Any]:
    resolved_dict = {}
    for key, value in values.items():
        resolved_value = resolve(value)
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
    return concatenate_functions.get(concat_type, lambda x: x)


@cache
def _get_concatenators() -> dict[
    ConcatenationType,
    Callable[[UnresolvedConcatenation], dict | list],
]:
    return {
        ConcatenationType(list, has_substitutions=False): _concatenate_lists,
        ConcatenationType(dict, has_substitutions=False): _concatenate_dicts,
    }


def _concatenate_dicts(values: UnresolvedConcatenation[dict]) -> dict:
    return _resolve_dict(reduce(merge, reversed(values)))


def _concatenate_lists(values: UnresolvedConcatenation) -> list:
    resolved_lists = [resolve(value) for value in values]
    return reduce(operator.iadd, resolved_lists, [])


def merge(superior: dict, inferior: dict) -> dict:
    """Merge two objects recursively. If keys overlap, merge values."""
    result = deepcopy(inferior)
    for key, value in superior.items():
        inferior_value = result.get(key)
        if inferior_value is None:
            result[key] = value
            continue
        result[key] = _ValueMerger.merge(inferior_value, value)
    return result


class _ValueMerger:
    duplication_elem = dict | list | UnresolvedSubstitution | UnresolvedConcatenation

    @classmethod
    def merge(
        cls,
        inferior: ANY_VALUE_TYPE | ANY_UNRESOLVED,
        superior: ANY_VALUE_TYPE | ANY_UNRESOLVED,
    ) -> ANY_VALUE_TYPE | ANY_UNRESOLVED:
        if isinstance(inferior, dict) and isinstance(superior, dict):
            return merge(superior, inferior)
        if isinstance(inferior, UnresolvedDuplication):
            return cls._merge_with_duplication(inferior, superior)
        if isinstance(inferior, cls.duplication_elem):
            return cls._merge_with_duplication_element(inferior, superior)
        return superior

    @classmethod
    def _merge_with_duplication(
        cls,
        inferior: UnresolvedDuplication,
        superior: ANY_VALUE_TYPE | ANY_UNRESOLVED,
    ) -> ANY_VALUE_TYPE | ANY_UNRESOLVED:
        if isinstance(superior, UnresolvedDuplication):
            inferior.extend(superior)
            return inferior
        if isinstance(superior, cls.duplication_elem):
            inferior.append(superior)
            return inferior
        return superior

    @classmethod
    def _merge_with_duplication_element(
        cls,
        inferior: "_ValueMerger.duplication_elem",
        superior: ANY_VALUE_TYPE | ANY_UNRESOLVED,
    ) -> ANY_VALUE_TYPE | ANY_UNRESOLVED:
        if isinstance(superior, UnresolvedDuplication):
            superior.insert(0, inferior)
            return superior
        if isinstance(superior, cls.duplication_elem):
            return UnresolvedDuplication([inferior, superior])
        return superior
