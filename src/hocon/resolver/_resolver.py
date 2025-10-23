import json
from collections.abc import Callable
from copy import deepcopy
from functools import reduce, singledispatchmethod
from typing import get_args

from hocon.constants import ANY_VALUE_TYPE, ROOT_TYPE, SIMPLE_VALUE_TYPE, UNDEFINED
from hocon.exceptions import HOCONConcatenationError, HOCONDeduplicationError
from hocon.resolver._simple_value import resolve_simple_value
from hocon.unresolved import (
    UnresolvedConcatenation,
    UnresolvedDuplication,
    UnresolvedSubstitution,
)

from . import _lazy_resolver
from ._substitution_resolver import SubstitutionResolver


def resolve(parsed: ROOT_TYPE) -> ROOT_TYPE:
    lazy_resolved = _lazy_resolver.resolve(parsed)
    resolver = Resolver(lazy_resolved)
    return resolver.resolve(lazy_resolved)


class Resolver:
    def __init__(self, parsed: ROOT_TYPE):
        self.resolve_substitution = SubstitutionResolver(parsed, self.resolve)

    @singledispatchmethod
    def resolve(self, values):
        raise NotImplementedError(f"Bad input value type: {type(values)}")

    @resolve.register
    def _(self, values: SIMPLE_VALUE_TYPE) -> ANY_VALUE_TYPE:
        return values

    @resolve.register
    def _(self, values: list) -> list:
        resolved_list = []
        for element in values:
            resolved_elem = self.resolve(element)
            if resolved_elem is not UNDEFINED:
                resolved_list.append(resolved_elem)
        return resolved_list

    @resolve.register
    def _(self, values: dict) -> dict:
        resolved_dict = {}
        for key, value in values.items():
            resolved_value = self.resolve(value)
            if resolved_value is not UNDEFINED:
                resolved_dict[key] = resolved_value
        return resolved_dict

    @resolve.register
    def _(self, values: UnresolvedSubstitution) -> ANY_VALUE_TYPE:
        return self.resolve_substitution(values)

    @resolve.register
    def _(self, values: UnresolvedConcatenation) -> ANY_VALUE_TYPE:
        values = self.resolve_substitutions(values)
        values = values.sanitize()
        if any(isinstance(value, (UnresolvedConcatenation, UnresolvedDuplication)) for value in values):
            raise HOCONConcatenationError("Something went horribly wrong. This is a bug.")
        if not values:
            return UNDEFINED
        if len(values) == 1 and type(values[0]) in get_args(SIMPLE_VALUE_TYPE) + (UnresolvedSubstitution,):
            return values[0]
        concat_type = values.get_type()
        concatenate_functions: dict[type[list | dict | str], Callable[[UnresolvedConcatenation], ANY_VALUE_TYPE]] = {
            list: self._concatenate_lists,
            dict: self._concatenate_dicts,
            str: self._concatenate_simple_values,
        }
        return concatenate_functions[concat_type](values)

    @resolve.register
    def _(self, values: UnresolvedDuplication) -> ANY_VALUE_TYPE:
        """Resolve duplication values starting from the last (latest overrides/merges with the rest).
        If it's a SIMPLE_VALUE_TYPE or a list, it overrides the rest.
        If it's a dict type, objects will merge.
        If at any point of object merging, duplicate value is not a dict, merging will stop.
        """
        if not values:
            raise HOCONDeduplicationError("Unresolved duplicate key must contain at least 1 element.")
        deduplicated = self._resolve_latest_unresolved_duplication_element(values)
        if not isinstance(deduplicated, dict):
            return deduplicated
        for value in reversed(values[:-1]):
            if isinstance(value, UnresolvedConcatenation):
                value = self.resolve(value)
            if isinstance(value, (dict, UnresolvedSubstitution)):
                deduplicated = self.merge(deduplicated, value)
            else:
                break
        return self.resolve(deduplicated)

    def _concatenate_dicts(self, values: UnresolvedConcatenation) -> dict:
        return self.resolve(reduce(self.merge, reversed(values)))

    def _concatenate_simple_values(self, values: UnresolvedConcatenation) -> str:
        if not all(isinstance(value, SIMPLE_VALUE_TYPE) for value in values):
            types = set([type(value) for value in values])
            raise HOCONConcatenationError(f"Concatenation of types {types} not allowed.")
        for i in range(len(values)):
            if not isinstance(values[i], str):
                values[i] = json.dumps(values[i])
        return resolve_simple_value(values)

    def _concatenate_lists(self, values: UnresolvedConcatenation) -> list:
        if not all([isinstance(value, list) for value in values]):
            raise HOCONConcatenationError("Something went horribly wrong. This is a bug.")
        resolved_lists = []
        for value in values:
            resolved_lists.append(self.resolve(value))
        return sum(resolved_lists, [])

    def _resolve_latest_unresolved_duplication_element(self, values: UnresolvedDuplication) -> ANY_VALUE_TYPE:
        while True:
            deduplicated = self.resolve(values[-1])
            if deduplicated is UNDEFINED:
                values.pop()
            else:
                break
        return deduplicated

    def merge(self, superior: dict, inferior: ANY_VALUE_TYPE | UnresolvedSubstitution) -> dict:
        """If both values are objects, then the objects are merged.
        If keys overlap, the latter wins.
        """
        if isinstance(inferior, UnresolvedSubstitution):
            inferior = self.resolve_substitution(inferior)
        if not isinstance(inferior, dict):
            return superior
        result = deepcopy(inferior)
        for key, value in superior.items():
            inferior_value = result.get(key)
            if isinstance(value, dict) and isinstance(inferior_value, dict):
                result[key] = self.merge(value, inferior_value)
            else:
                resolved_value = self.resolve(value)
                if resolved_value is not UNDEFINED:
                    result[key] = resolved_value
        return result

    def resolve_substitutions(self, values: UnresolvedConcatenation) -> UnresolvedConcatenation:
        values_with_resolved_substitutions = UnresolvedConcatenation()
        for value in values:
            if isinstance(value, UnresolvedSubstitution):
                value = self.resolve_substitution(value)
            values_with_resolved_substitutions.append(value)
        return values_with_resolved_substitutions
