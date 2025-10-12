import os
from typing import Any, Optional

from ._substitution import SubstitutionStatus, Substitution
from ..constants import WHITE_CHARS, UNDEFINED
from ..exceptions import HOCONConcatenationError
from ..strings import UnquotedString, QuotedString
from ..unresolved import UnresolvedConcatenation, UnresolvedSubstitution


def sanitize_unresolved_concatenation(concatenation: UnresolvedConcatenation) -> UnresolvedConcatenation:
    concatenation = _filter_out_undefined_substitutions(concatenation)
    if any(isinstance(value, list) for value in concatenation):
        concatenation = filter_out_unquoted_space(concatenation)
        if not all(isinstance(value, list | UnresolvedSubstitution) for value in concatenation):
            raise HOCONConcatenationError(f"Arrays (lists) mixed with other value types not allowed")
    if any(isinstance(value, dict) for value in concatenation):
        concatenation = filter_out_unquoted_space(concatenation)
        if not all(isinstance(value, dict | UnresolvedSubstitution) for value in concatenation):
            raise HOCONConcatenationError(f"Objects (dictionaries) mixed with other value types not allowed")
    if any(isinstance(value, str) for value in concatenation):
        concatenation = _strip_unquoted_space(concatenation)
    return concatenation


def _filter_out_undefined_substitutions(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    return UnresolvedConcatenation(filter(lambda v: v is not UNDEFINED, values))


def filter_out_unquoted_space(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    return UnresolvedConcatenation(filter(lambda v: not _is_empty_unquoted_string(v), values))


def _is_empty_unquoted_string(value: Any) -> bool:
    """Is given value an UnquotedString containing nothing or WHITE_CHARS only"""
    return isinstance(value, UnquotedString) and not value.strip(WHITE_CHARS)


def _strip_unquoted_space(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    try:
        first = next(index for index, value in enumerate(values) if not _is_empty_unquoted_string(value))
    except StopIteration:
        return UnresolvedConcatenation([])
    last = -1 * next(index for index, value in enumerate(reversed(values)) if not _is_empty_unquoted_string(value))
    if last == 0:
        return UnresolvedConcatenation(values[first:])
    return UnresolvedConcatenation(values[first:last])


def get_from_env(substitution: UnresolvedSubstitution) -> Substitution:
    env_value: Optional[str] = os.getenv(".".join(substitution.keys))
    if env_value is None:
        return Substitution(value=UNDEFINED, status=SubstitutionStatus.UNDEFINED)
    return Substitution(value=QuotedString(env_value), status=SubstitutionStatus.RESOLVED)
