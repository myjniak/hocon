from functools import reduce
from itertools import chain
from typing import Callable, Any
from functools import singledispatchmethod
from ..constants import ANY_VALUE_TYPE, ROOT_TYPE, ANY_UNRESOLVED, UNDEFINED
from ..exceptions import HOCONConcatenationError, HOCONDuplicateKeyMergeError, HOCONSubstitutionUndefinedError
from ..resolver._simple_value import resolve_simple_value
from ..resolver._utils import filter_out_unquoted_space, sanitize_unresolved_concatenation, \
    cut_self_reference_and_fields_that_override_it, get_from_env, Substitution, SubstitutionStatus
from ..unresolved import UnresolvedConcatenation, UnresolvedDuplicateValue, UnresolvedSubstitution


def resolve(parsed: ROOT_TYPE) -> ROOT_TYPE:
    if isinstance(parsed, list):
        return Resolver(parsed).resolve_list(parsed)
    else:
        return Resolver(parsed).resolve_dict(parsed)


class Resolver:
    def __init__(self, parsed: ROOT_TYPE):
        self._parsed = parsed
        self.substitutions: dict[int, Substitution] = {}
        self.lazy = False

    @property
    def parsed(self):
        return self._parsed

    def get_resolver(self, element: Any) -> Callable[[Any], Any]:
        if self.lazy:
            resolver_map: dict[str, Callable[[Any], Any]] = {
                "dict": self.resolve_dict,
                "list": self.resolve_list,
                "UnresolvedConcatenation": self.concatenate,
                "UnresolvedDuplicateValue": self.deduplicate
            }
        else:
            resolver_map: dict[str, Callable[[Any], Any]] = {
                "dict": self.resolve_dict,
                "list": self.resolve_list,
                "UnresolvedConcatenation": self.resolve_substitutions_and_concatenate,
                "UnresolvedDuplicateValue": self.deduplicate,
                "UnresolvedSubstitution": self.resolve_substitution
            }
        return resolver_map.get(type(element).__name__, lambda x: x)

    def resolve_list(self, values: list) -> list:
        resolved_list = []
        for element in values:
            func = self.get_resolver(element)
            resolved_elem = func(element)
            if resolved_elem is not UNDEFINED:
                resolved_list.append(resolved_elem)
        return resolved_list

    def resolve_dict(self, dictionary: dict) -> dict:
        resolved_dict = {}
        for key, value in dictionary.items():
            func = self.get_resolver(value)
            resolved_value = func(value)
            if resolved_value is not UNDEFINED:
                resolved_dict[key] = resolved_value
        return resolved_dict

    def resolve_value(self, value: Any) -> ANY_VALUE_TYPE:
        func = self.get_resolver(value)
        return func(value)

    def resolve_substitutions_and_concatenate(self, values: UnresolvedConcatenation) -> ANY_VALUE_TYPE:
        values = self.resolve_substitutions(values)
        return self.concatenate(values)

    def concatenate(self, values: UnresolvedConcatenation) -> ANY_VALUE_TYPE:
        values = sanitize_unresolved_concatenation(values)
        if not values:
            return UNDEFINED
        if any(isinstance(value, (UnresolvedConcatenation, UnresolvedDuplicateValue)) for value in values):
            raise HOCONConcatenationError("Something went horribly wrong. This is a bug.")
        if all(isinstance(value, str) for value in values):
            return resolve_simple_value(values)
        if any(isinstance(value, list) for value in values):
            return self._concatenate_lists(values)
        if any(isinstance(value, dict) for value in values):
            return self.resolve_value(reduce(self.merge, reversed(values)))
        if len(values) == 1:
            return values[0]
        raise HOCONConcatenationError(f"Multiple types concatenation not allowed: {values}")

    def _concatenate_lists(self, values: UnresolvedConcatenation) -> list:
        resolved_lists = []
        for value in values:
            if isinstance(value, list):
                resolved_lists.append(self.resolve_list(value))
            elif isinstance(value, UnresolvedSubstitution):
                resolved_list = self.resolve_substitution(value)
                if resolved_list is UNDEFINED:
                    continue
                if not isinstance(resolved_list, list):
                    raise HOCONConcatenationError(
                        f"Attempted list concatenation with substitution {value} "
                        f"that resolved to {type(resolved_list)}.")
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

    def resolve_substitutions(self, values: UnresolvedConcatenation) -> UnresolvedConcatenation:
        values_with_resolved_substitutions = UnresolvedConcatenation()
        for value in values:
            if isinstance(value, UnresolvedSubstitution):
                values_with_resolved_substitutions.append(self.resolve_substitution(value))
            else:
                values_with_resolved_substitutions.append(value)
        return values_with_resolved_substitutions

    def resolve_substitution(self, substitution: UnresolvedSubstitution) -> ANY_VALUE_TYPE:
        resolved_sub = self.substitutions.get(substitution.identifier, Substitution())
        if resolved_sub.status == SubstitutionStatus.RESOLVED:
            return resolved_sub.value
        if resolved_sub.status == SubstitutionStatus.RESOLVING:
            result = self.resolve_sustitution_fallback(substitution)
            resolved_sub.value = result
            resolved_sub.status = SubstitutionStatus.RESOLVED
            self.substitutions[substitution.identifier] = resolved_sub
            self.lazy = False
            return result
            # raise HOCONSubstitutionCycleError(f"Could not resolve {substitution}")
        self.lazy = True
        self.substitutions[substitution.identifier] = Substitution(status=SubstitutionStatus.RESOLVING)
        subvalue = self.parsed
        for key in substitution.keys:
            if isinstance(subvalue, ANY_UNRESOLVED):
                subvalue = self.resolve_value(subvalue)
            elif isinstance(subvalue, list) and key.isdigit():
                subvalue = subvalue[int(key)]
                subvalue = self.resolve_value(subvalue)
            elif isinstance(subvalue, dict) and key in subvalue:
                subvalue = subvalue[key]
                subvalue = self.resolve_value(subvalue)
            else:
                resolved_sub = get_from_env(substitution)
                if resolved_sub.status == SubstitutionStatus.UNDEFINED and substitution.optional is False:
                    raise HOCONSubstitutionUndefinedError(f"Undefined substitution {substitution}.")
                self.substitutions[substitution.identifier] = resolved_sub
                self.lazy = False
                return resolved_sub.value
        if self.substitutions[substitution.identifier].status == SubstitutionStatus.RESOLVED:
            return self.substitutions[substitution.identifier].value
        if isinstance(subvalue, UnresolvedSubstitution):
            subvalue = self.resolve_substitution(subvalue)
        resolved_sub.value = subvalue
        resolved_sub.status = SubstitutionStatus.RESOLVED
        self.substitutions[substitution.identifier] = resolved_sub
        self.lazy = False
        return subvalue

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

    def resolve_sustitution_fallback(self, substitution: UnresolvedSubstitution) -> ANY_VALUE_TYPE:
        """In case of self-referencial substitutions, try to resolve them by removing the self-reference, and
        nodes after that.
        For example for:

        a : { a : { c : 1 } }
        b : 1
        a : ${a.a}
        a : { a : 2 }
        b : 5

        Substitution ${a.a} will be attempted to resolve with the following object:
        a : { a : { c : 1 } }
        b : 1
        b : 5
        And ultimately return {c:1}
        """
        carved_parsed = cut_self_reference_and_fields_that_override_it(substitution, self.parsed)
        result = Resolver(carved_parsed).resolve_substitution(substitution)
        return result
