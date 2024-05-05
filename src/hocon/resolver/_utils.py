import os
from copy import deepcopy
from typing import Any, Optional

from ..constants import WHITE_CHARS, ROOT_TYPE
from ..exceptions import HOCONConcatenationError, HOCONSubstitutionUndefinedError
from ..strings import UnquotedString, QuotedString
from ..unresolved import UnresolvedConcatenation, UnresolvedSubstitution, UnresolvedDuplicateValue


def sanitize_unresolved_concatenation(concatenation: UnresolvedConcatenation) -> UnresolvedConcatenation:
    if any(isinstance(value, list) for value in concatenation):
        concatenation = filter_out_unquoted_space(concatenation)
        if not all(isinstance(value, list | UnresolvedSubstitution) for value in concatenation):
            raise HOCONConcatenationError(f"Arrays (lists) mixed with other value types not allowed")
    if any(isinstance(value, dict) for value in concatenation):
        concatenation = filter_out_unquoted_space(concatenation)
        if not all(isinstance(value, dict | UnresolvedSubstitution) for value in concatenation):
            raise HOCONConcatenationError(f"Objects (dictionaries) mixed with other value types not allowed")
    if any(isinstance(value, str) for value in concatenation):
        concatenation = strip_unquoted_space(concatenation)
    return concatenation


def filter_out_unquoted_space(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    return UnresolvedConcatenation(
        filter(lambda value: not isinstance(value, UnquotedString) or value.strip(WHITE_CHARS), values)
    )


def strip_unquoted_space(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    def is_unquoted_string_with_space_only(value: Any) -> bool:
        return isinstance(value, UnquotedString) and not value.strip(WHITE_CHARS)

    first = next(index for index, value in enumerate(values) if not is_unquoted_string_with_space_only(value))
    last = -1 * next(index for index, value in enumerate(reversed(values)) if not is_unquoted_string_with_space_only(value))
    if last == 0:
        return UnresolvedConcatenation(values[first:])
    return UnresolvedConcatenation(values[first:last])


def get_from_env(value: UnresolvedSubstitution) -> str:
    value: Optional[str] = os.getenv(".".join(value.keys))
    if value is None:
        raise HOCONSubstitutionUndefinedError(f"Undefined substitution {value}.")
    return QuotedString(value)


def cut_self_reference_and_fields_that_override_it(substitution: UnresolvedSubstitution, parsed: ROOT_TYPE) -> ROOT_TYPE:
    def _cut(sub: UnresolvedSubstitution, subtree: Any, keypath_index: int = 0):
        for i, key in enumerate(sub.keys[keypath_index:]):
            if isinstance(subtree, (UnresolvedConcatenation, UnresolvedDuplicateValue)):
                for index, item in enumerate(subtree):
                    job_done = _cut(sub, item, i)
                    if item == sub or job_done:
                        for _ in range(len(subtree) - index):
                            subtree.pop()
                        return True
            elif isinstance(subtree, dict) and key in subtree:
                subtree = subtree[key]
            elif isinstance(subtree, list) and key.isdigit():
                subtree = subtree[int(key)]
        if isinstance(subtree, (UnresolvedConcatenation, UnresolvedDuplicateValue)):
            for index, item in enumerate(subtree):
                if item == sub or (isinstance(item, list) and sub in item):
                    for _ in range(len(subtree) - index):
                        subtree.pop()
                    return True

    carved_parsed = deepcopy(parsed)
    _cut(substitution, carved_parsed)
    return carved_parsed
