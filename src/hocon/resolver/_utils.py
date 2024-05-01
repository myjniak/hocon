from typing import Any

from ._simple_value import _strip_string_list
from ..constants import WHITE_CHARS
from ..exceptions import HOCONConcatenationError
from ..strings import UnquotedString
from ..unresolved import UnresolvedConcatenation


def sanitize_unresolved_concatenation(concatenation: UnresolvedConcatenation) -> UnresolvedConcatenation:
    if any(isinstance(value, list) for value in concatenation):
        concatenation = filter_out_unquoted_space(concatenation)
        if not all(isinstance(value, list) for value in concatenation):
            raise HOCONConcatenationError(f"Arrays (lists) mixed with other value types not allowed")
    if any(isinstance(value, dict) for value in concatenation):
        concatenation = filter_out_unquoted_space(concatenation)
        if not all(isinstance(value, dict) for value in concatenation):
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
