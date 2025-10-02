from typing import Callable, Any

from hocon.constants import ANY_VALUE_TYPE, ANY_UNRESOLVED, ROOT_TYPE
from hocon.exceptions import HOCONSubstitutionUndefinedError, HOCONSubstitutionCycleError
from hocon.resolver._utils import cut_self_reference_and_fields_that_override_it, SubstitutionStatus, get_from_env, \
    Substitution
from hocon.unresolved import UnresolvedSubstitution


class SubstitutionResolver:
    def __init__(self, parsed: ROOT_TYPE, resolve_value_func: Callable[[Any], ANY_VALUE_TYPE], lazy_resolve_value_func: Callable[[Any], ANY_VALUE_TYPE], substitutions: dict[int, Substitution] = None):
        self._parsed = parsed
        self.resolve_value = resolve_value_func
        self.lazy_resolve_value = lazy_resolve_value_func
        self.subs: dict[int, Substitution] = substitutions or {}

    def __call__(self, substitution: UnresolvedSubstitution) -> ANY_VALUE_TYPE:
        cached_sub = self.subs.get(substitution.id_, Substitution())
        if cached_sub.status == SubstitutionStatus.RESOLVED:
            return cached_sub.value
        if cached_sub.status == SubstitutionStatus.RESOLVING:
            cached_sub.status = SubstitutionStatus.FALLBACK_UNRESOLVED
            result = self.resolve_substitution_fallback(substitution)
            self.subs[substitution.id_] = Substitution(value=result, status=SubstitutionStatus.RESOLVED)
            return result
        self._turn_to_resolving_state(substitution, cached_sub.status)
        subvalue = self._try_resolve(substitution)
        if self.subs[substitution.id_].status == SubstitutionStatus.RESOLVED:
            return self.subs[substitution.id_].value

        ## gdzieś tu for key in substitution.root + substitution.keys

        self.subs[substitution.id_] = Substitution(value=subvalue, status=SubstitutionStatus.RESOLVED)
        return subvalue

    def _try_resolve(self, substitution: UnresolvedSubstitution) -> ANY_VALUE_TYPE:
        value = self._parsed
        for key in substitution.keys:
            if isinstance(value, ANY_UNRESOLVED):
                value = self.resolve_value(value)
            if isinstance(value, dict) and key in value:
                value = self.lazy_resolve_value(value[key])
            elif isinstance(value, ROOT_TYPE):
                value = self._resolve_sub_from_env(substitution)
        if isinstance(value, ROOT_TYPE):
            value = self.resolve_value(value)
        if isinstance(value, UnresolvedSubstitution):
            value = self(value)
        return value

    def _turn_to_resolving_state(self, substitution: UnresolvedSubstitution, status: SubstitutionStatus) -> None:
        exc = HOCONSubstitutionCycleError(f"Could not resolve {substitution}.")
        new_status = status.to_resolving(exc)
        self.subs[substitution.id_] = Substitution(status=new_status)

    def _resolve_sub_from_env(self, substitution: UnresolvedSubstitution) -> ANY_VALUE_TYPE:
        resolved_sub = get_from_env(substitution)
        if resolved_sub.status == SubstitutionStatus.UNDEFINED and substitution.optional is False:
            resolving_status = self.subs[substitution.id_].status
            if (
                    resolving_status == SubstitutionStatus.FALLBACK_RESOLVING
                    and substitution.keys != substitution.location
                    and substitution.keys != substitution.relative_location
            ):
                raise HOCONSubstitutionCycleError(f"Cycle occurred when resolving {substitution}")
            else:
                raise HOCONSubstitutionUndefinedError(f"Could not resolve substitution {substitution}.")
        self.subs[substitution.id_] = resolved_sub
        return resolved_sub.value

    def resolve_substitution_fallback(self, substitution: UnresolvedSubstitution) -> ANY_VALUE_TYPE:
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
        carved_parsed = cut_self_reference_and_fields_that_override_it(substitution, self._parsed)
        sub_resolver = SubstitutionResolver(carved_parsed, resolve_value_func=self.resolve_value, lazy_resolve_value_func=self.lazy_resolve_value, substitutions=self.subs)
        result = sub_resolver(substitution)
        return result