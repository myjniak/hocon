import json
from copy import deepcopy
from dataclasses import dataclass
from functools import reduce, singledispatchmethod
from typing import Callable, Any, Type, get_args

from ._substitution_resolver import SubstitutionResolver
from ..constants import ANY_VALUE_TYPE, ROOT_TYPE, UNDEFINED, SIMPLE_VALUE_TYPE
from ..exceptions import (
    HOCONConcatenationError,
    HOCONDeduplicationError,
)
from ..resolver._simple_value import resolve_simple_value
from ..unresolved import UnresolvedConcatenation, UnresolvedDuplication, UnresolvedSubstitution, ANY_UNRESOLVED


def resolve(parsed: ROOT_TYPE) -> ROOT_TYPE:
    lazy_resolver = LazyResolver()
    lazy_resolved = lazy_resolver.resolve(parsed)
    resolver = Resolver(lazy_resolved)
    return resolver.resolve(lazy_resolved)


class Resolver:
    def __init__(self, parsed: ROOT_TYPE):
        self.resolve_substitution = SubstitutionResolver(parsed, self.resolve_value)

    def resolve_value(self, value: Any) -> ANY_VALUE_TYPE:
        func = self.get_resolver(value)
        return func(value)

    def get_resolver(self, element: Any) -> Callable[[Any], Any]:
        resolver_map: dict[Type, Callable[[Any], Any]] = {
            dict: self.resolve,
            list: self.resolve,
            UnresolvedConcatenation: self.resolve,
            UnresolvedDuplication: self.resolve,
            UnresolvedSubstitution: self.resolve_substitution,
        }
        return resolver_map.get(type(element), lambda x: x)

    @singledispatchmethod
    def resolve(self, values):
        raise NotImplementedError(f"Bad input value type: {type(values)}")

    @resolve.register
    def _(self, values: list) -> list:
        resolved_list = []
        for element in values:
            resolve_ = self.get_resolver(element)
            resolved_elem = resolve_(element)
            if resolved_elem is not UNDEFINED:
                resolved_list.append(resolved_elem)
        return resolved_list

    @resolve.register
    def _(self, dictionary: dict) -> dict:
        resolved_dict = {}
        for key, value in dictionary.items():
            resolve_ = self.get_resolver(value)
            resolved_value = resolve_(value)
            if resolved_value is not UNDEFINED:
                resolved_dict[key] = resolved_value
        return resolved_dict

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
        concatenate_functions: dict[Type[list | dict | str], Callable[[UnresolvedConcatenation], ANY_VALUE_TYPE]] = {
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
                value = self.resolve_value(value)
            if isinstance(value, (dict, UnresolvedSubstitution)):
                deduplicated = self.merge(deduplicated, value)
            else:
                break
        return self.resolve_value(deduplicated)

    def _concatenate_dicts(self, values: UnresolvedConcatenation) -> dict:
        return self.resolve_value(reduce(self.merge, reversed(values)))

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
            deduplicated = self.resolve_value(values[-1])
            if deduplicated is UNDEFINED:
                values.pop()
            else:
                break
        return deduplicated

    def merge(self, superior: dict, inferior: dict | UnresolvedSubstitution) -> dict:
        """If both values are objects, then the objects are merged.
        If keys overlap, the latter wins."""
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
                resolved_value = self.resolve_value(value)
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


class LazyResolver:
    def __init__(self):
        pass

    def resolve_value(self, value: Any) -> ANY_VALUE_TYPE:
        func = self.get_resolver(value)
        return func(value)

    def get_resolver(self, element: Any) -> Callable[[Any], Any]:
        resolver_map: dict[Type, Callable[[Any], Any]] = {
            dict: self.resolve,
            list: self.resolve,
            UnresolvedConcatenation: self.concatenate,
            UnresolvedDuplication: self.deduplicate,
        }
        return resolver_map.get(type(element), lambda x: x)

    @singledispatchmethod
    def resolve(self, values):
        raise NotImplementedError(f"Bad input value type: {type(values)}")

    @resolve.register
    def _(self, values: list) -> list:
        resolved_list = []
        for element in values:
            resolve_ = self.get_resolver(element)
            resolved_elem = resolve_(element)
            if resolved_elem is not UNDEFINED:
                resolved_list.append(resolved_elem)
        return resolved_list

    @resolve.register
    def _(self, dictionary: dict) -> dict:
        resolved_dict = {}
        for key, value in dictionary.items():
            resolve_ = self.get_resolver(value)
            resolved_value = resolve_(value)
            if resolved_value is not UNDEFINED:
                resolved_dict[key] = resolved_value
        return resolved_dict

    def concatenate(self, values: UnresolvedConcatenation) -> ANY_VALUE_TYPE | UnresolvedConcatenation:
        values = values.sanitize()
        if not values:
            return UNDEFINED
        if len(values) == 1 and type(values[0]) in get_args(SIMPLE_VALUE_TYPE) + (UnresolvedSubstitution,):
            return values[0]
        concatenate_function = self._get_concatenator(values)
        if concatenate_function is not None:
            return concatenate_function(values)
        raise HOCONConcatenationError(f"Concatenation not allowed: {values}")

    def _get_concatenator(self, values: UnresolvedConcatenation) -> Callable[[UnresolvedConcatenation], ANY_VALUE_TYPE]:
        @dataclass(frozen=True)
        class ConcatenationType:
            type: Type[list | dict | str]
            has_substitutions: bool

        concat_type = ConcatenationType(type=values.get_type(), has_substitutions=values.has_substitutions())
        concatenate_functions: dict[ConcatenationType, Callable[[UnresolvedConcatenation], ANY_VALUE_TYPE]] = {
            ConcatenationType(list, True): self._concatenate_lists_with_subs,
            ConcatenationType(dict, True): self._concatenate_dicts_with_subs,
            ConcatenationType(str, True): self._concatenate_simple_values_with_subs,
            ConcatenationType(list, False): self._concatenate_lists,
            ConcatenationType(dict, False): self._concatenate_dicts,
            ConcatenationType(str, False): self._concatenate_simple_values,
        }
        return concatenate_functions.get(concat_type)

    def _concatenate_dicts_with_subs(self, values: UnresolvedConcatenation) -> UnresolvedConcatenation:
        return reduce(self.merge_dict_concatenation, reversed(values))

    def _concatenate_dicts(self, values: UnresolvedConcatenation) -> dict:
        return self.resolve_value(reduce(self.merge, reversed(values)))

    def _concatenate_simple_values_with_subs(self, values: UnresolvedConcatenation) -> UnresolvedConcatenation:
        """[${a}, b, c, ${d}, e, f, g] should turn to [${a}, bc, ${d}, efg]"""
        result = UnresolvedConcatenation()
        chunks_to_concatenate = []
        for value in values:
            if isinstance(value, UnresolvedSubstitution):
                if chunks_to_concatenate:
                    if len(chunks_to_concatenate) == 1:
                        result.append(chunks_to_concatenate[0])
                    else:
                        result.append(
                            self._concatenate_simple_values(
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
                result.append(
                    self._concatenate_simple_values(UnresolvedConcatenation(chunks_to_concatenate), strip_left=False)
                )
        return result

    def _concatenate_simple_values(
        self, values: UnresolvedConcatenation, strip_left: bool = True, strip_right: bool = True
    ) -> str:
        if not all(isinstance(value, str) for value in values):
            types = set([type(value) for value in values])
            raise HOCONConcatenationError(f"Lazy concatenation of types {types} not allowed.")
        values = list(filter(lambda item: item is not UNDEFINED, values))
        return resolve_simple_value(values, strip_left=strip_left, strip_right=strip_right)

    def _concatenate_lists_with_subs(self, values: UnresolvedConcatenation) -> UnresolvedConcatenation:
        result = UnresolvedConcatenation()
        chunks_to_concatenate = []
        for value in values:
            if isinstance(value, UnresolvedSubstitution):
                if chunks_to_concatenate:
                    result.append(self._concatenate_lists(UnresolvedConcatenation(chunks_to_concatenate)))
                    chunks_to_concatenate = []
                result.append(value)
                continue
            chunks_to_concatenate.append(value)
        if chunks_to_concatenate:
            result.append(self._concatenate_lists(UnresolvedConcatenation(chunks_to_concatenate)))
        return result

    def _concatenate_lists(self, values: UnresolvedConcatenation) -> list:
        if not all([isinstance(value, list) for value in values]):
            raise HOCONConcatenationError("Something went horribly wrong. This is a bug.")
        resolved_lists = []
        for value in values:
            resolved_lists.append(self.resolve(value))
        return sum(resolved_lists, [])

    def deduplicate(self, values: UnresolvedDuplication) -> ANY_VALUE_TYPE | UnresolvedDuplication:
        """Resolve duplication values starting from the last (latest overrides/merges with the rest).
        If it's a SIMPLE_VALUE_TYPE or a list, it overrides the rest.
        If it's a dict type, objects will merge.
        If at any point of object merging, duplicate value is not a dict, merging will stop.
        """
        values = values.sanitize()
        last_value = self.resolve_value(values[-1])
        deduplicated = UnresolvedDuplication([last_value])
        if not isinstance(last_value, (dict, ANY_UNRESOLVED)):
            return last_value
        for value in reversed(values[:-1]):
            value = self.resolve_value(value)
            if isinstance(value, ANY_UNRESOLVED) or isinstance(deduplicated[0], ANY_UNRESOLVED):
                deduplicated.insert(0, value)
            elif isinstance(value, dict):
                if isinstance(deduplicated[0], dict):
                    deduplicated[0] = self.merge(deduplicated[0], value)
                else:
                    deduplicated.insert(0, value)
            else:
                break
        if len(deduplicated) == 1:
            return deduplicated[0]
        return deduplicated

    @singledispatchmethod
    def merge_dict_concatenation(
        self, superior, inferior: dict | UnresolvedSubstitution
    ) -> dict | UnresolvedConcatenation:
        raise NotImplementedError(f"Bad input value type: {type(superior)}")

    @merge_dict_concatenation.register(UnresolvedSubstitution)
    def _(self, superior: UnresolvedSubstitution, inferior: dict | UnresolvedSubstitution) -> UnresolvedConcatenation:
        return UnresolvedConcatenation([inferior, superior])

    @merge_dict_concatenation.register(dict)
    def _(self, superior: dict, inferior: dict | UnresolvedSubstitution) -> dict | UnresolvedConcatenation:
        if isinstance(inferior, dict):
            return self.merge(superior, inferior)
        return UnresolvedConcatenation([inferior, superior])

    @merge_dict_concatenation.register(UnresolvedConcatenation)
    def _(
        self, superior: UnresolvedConcatenation, inferior: dict | UnresolvedSubstitution
    ) -> dict | UnresolvedConcatenation:
        if isinstance(superior[0], dict) and isinstance(inferior, dict):
            superior[0] = self.merge(superior[0], inferior)
        else:
            superior.insert(0, inferior)
        return superior

    def merge(self, superior: dict, inferior: dict) -> dict | UnresolvedConcatenation:
        """If both values are objects, then the objects are merged.
        If keys overlap, the latter wins."""
        result = deepcopy(inferior)
        for key, value in superior.items():
            inferior_value = result.get(key)
            if isinstance(inferior_value, ANY_UNRESOLVED):
                inferior_value = self.resolve_value(inferior_value)
            if isinstance(value, dict) and isinstance(inferior_value, dict):
                result[key] = self.merge(value, inferior_value)
            else:
                resolved_value = self.resolve_value(value)
                if resolved_value is not UNDEFINED:
                    result[key] = resolved_value
        return result
