import json
from functools import reduce
from functools import singledispatchmethod
from itertools import chain
from typing import Callable, Any, Type, get_args

from ._substitution_resolver import SubstitutionResolver
from ..constants import ANY_VALUE_TYPE, ROOT_TYPE, UNDEFINED, SIMPLE_VALUE_TYPE
from ..exceptions import (
    HOCONConcatenationError,
    HOCONDuplicateKeyMergeError,
)
from ..resolver._simple_value import resolve_simple_value
from ..resolver._utils import (
    filter_out_unquoted_space,
    sanitize_unresolved_concatenation,
)
from ..unresolved import UnresolvedConcatenation, UnresolvedDuplicateValue, UnresolvedSubstitution


def resolve(parsed: ROOT_TYPE) -> ROOT_TYPE:
    resolver = Resolver(parsed)
    return resolver.resolve(parsed)


class Resolver:
    def __init__(self, parsed: ROOT_TYPE):
        self._parsed = parsed
        self.lazy: bool = False
        self.resolve_substitution = SubstitutionResolver(parsed, self.resolve_value, self.lazy_resolve_value)

    @property
    def parsed(self):
        return self._parsed

    def get_resolver(self, element: Any) -> Callable[[Any], Any]:
        if self.lazy:
            resolver_map: dict[Type, Callable[[Any], Any]] = {
                dict: self.resolve,
                list: self.resolve,
                UnresolvedConcatenation: self.concatenate,
                UnresolvedDuplicateValue: self.deduplicate,
            }
        else:
            resolver_map: dict[Type, Callable[[Any], Any]] = {
                dict: self.resolve,
                list: self.resolve,
                UnresolvedConcatenation: self.resolve_substitutions_and_concatenate,
                UnresolvedDuplicateValue: self.deduplicate,
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

    def lazy_resolve_value(self, value: Any) -> ANY_VALUE_TYPE:
        self.lazy = True
        result = self.resolve_value(value)
        self.lazy = False
        return result

    def resolve_value(self, value: Any) -> ANY_VALUE_TYPE:
        func = self.get_resolver(value)
        return func(value)

    def resolve_substitutions_and_concatenate(self, values: UnresolvedConcatenation) -> ANY_VALUE_TYPE:
        values = self.resolve_substitutions(values)
        return self.concatenate(values)

    def concatenate(self, values: UnresolvedConcatenation) -> ANY_VALUE_TYPE:
        values = sanitize_unresolved_concatenation(values)
        if any(isinstance(value, (UnresolvedConcatenation, UnresolvedDuplicateValue)) for value in values):
            raise HOCONConcatenationError("Something went horribly wrong. This is a bug.")
        if not values:
            return UNDEFINED
        if len(values) == 1 and type(values[0]) in get_args(SIMPLE_VALUE_TYPE) + (UnresolvedSubstitution,):
            return values[0]
        concat_type = self._get_concatenation_type(values)
        concatenate_functions: dict[Type[list | dict | str], Callable[[UnresolvedConcatenation], ANY_VALUE_TYPE]] = {
            list: self._concatenate_lists,
            dict: self._concatenate_dicts,
            str: self._concatenate_simple_values,
        }
        concatenate_function = concatenate_functions.get(concat_type)
        if concatenate_function is not None:
            return concatenate_functions[concat_type](values)
        raise HOCONConcatenationError(f"Multiple types concatenation not allowed: {values}")

    @staticmethod
    def _get_concatenation_type(values: UnresolvedConcatenation) -> Type[list | dict | str]:
        concat_types = set(type(value) for value in values)
        concat_types.discard(UnresolvedSubstitution)
        if all(issubclass(concat_type, SIMPLE_VALUE_TYPE) for concat_type in concat_types):
            return str
        if len(concat_types) > 1:
            raise HOCONConcatenationError(f"Multiple types concatenation not allowed: {concat_types}")
        return concat_types.pop()

    def _concatenate_dicts(self, values: UnresolvedConcatenation) -> dict:
        return self.resolve_value(reduce(self.merge, reversed(values)))

    def _concatenate_simple_values(self, values: UnresolvedConcatenation) -> str:
        for i in range(len(values)):
            if isinstance(values[i], UnresolvedSubstitution):
                values[i] = self.resolve_substitution(values[i])
            if values[i] is UNDEFINED:
                continue
            if not isinstance(values[i], SIMPLE_VALUE_TYPE):
                raise HOCONConcatenationError(f"Multiple types concatenation not allowed: {values}")
            if not isinstance(values[i], str):
                values[i] = json.dumps(values[i])
        values = list(filter(lambda item: item is not UNDEFINED, values))
        return resolve_simple_value(values)

    def _concatenate_lists(self, values: UnresolvedConcatenation) -> list:
        resolved_lists = []
        for value in values:
            if isinstance(value, list):
                resolved_lists.append(self.resolve(value))
            elif isinstance(value, UnresolvedSubstitution):
                resolved_list = self.resolve_substitution(value)
                if resolved_list is UNDEFINED:
                    continue
                if not isinstance(resolved_list, list):
                    raise HOCONConcatenationError(
                        f"Attempted list concatenation with substitution {value} "
                        f"that resolved to {type(resolved_list)}."
                    )
                resolved_lists.append(resolved_list)
            else:
                raise HOCONConcatenationError("Something went horribly wrong. This is a bug.")
        return sum(resolved_lists, [])

    def deduplicate(self, values: UnresolvedDuplicateValue) -> ANY_VALUE_TYPE:
        while True:
            if not values:
                raise HOCONDuplicateKeyMergeError("Unresolved duplicate key must contain at least 2 elements.")
            deduplicated = self.resolve_value(values[-1])
            if deduplicated is UNDEFINED:
                values.pop()
            else:
                break
        for value in reversed(values[:-1]):
            if isinstance(deduplicated, dict) and isinstance(value, UnresolvedConcatenation):
                value = filter_out_unquoted_space(value)
                if all(isinstance(elem, (dict, UnresolvedSubstitution)) for elem in value):
                    deduplicated = reduce(self.merge, chain([deduplicated], reversed(value)))
                else:
                    break
            elif isinstance(deduplicated, dict) and isinstance(value, (dict, UnresolvedSubstitution)):
                deduplicated = self.merge(deduplicated, value)
            else:
                break
        return self.resolve_value(deduplicated)

    def merge(self, superior: dict, inferior: dict | UnresolvedSubstitution) -> dict:
        """If both values are objects, then the objects are merged.
        If keys overlap, the latter wins."""
        if isinstance(inferior, UnresolvedSubstitution):
            inferior = self.resolve_substitution(inferior)
        if not isinstance(inferior, dict):
            return superior

        for key, value in superior.items():
            if isinstance(value, dict) and isinstance(inferior.get(key), dict):
                inferior[key] = self.merge(value, inferior[key])
            else:
                resolved_value = self.resolve_value(value)
                if resolved_value is not UNDEFINED:
                    inferior[key] = resolved_value
        return inferior

    def resolve_substitutions(self, values: UnresolvedConcatenation) -> UnresolvedConcatenation:
        values_with_resolved_substitutions = UnresolvedConcatenation()
        for value in values:
            if isinstance(value, UnresolvedSubstitution):
                value = self.resolve_substitution(value)
            values_with_resolved_substitutions.append(value)
        return values_with_resolved_substitutions
