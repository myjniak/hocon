from typing import Type

from ..constants import ANY_VALUE_TYPE, WHITE_CHARS
from ..strings import UnquotedString
from ..unresolved import UnresolvedConcatenation


def filter_out_unquoted_space(values: UnresolvedConcatenation) -> UnresolvedConcatenation:
    return UnresolvedConcatenation(
        filter(lambda value: not isinstance(value, UnquotedString) or value.strip(WHITE_CHARS), values)
    )
