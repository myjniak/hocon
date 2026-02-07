"""Utils for dictionary value / list element evaluation."""

from copy import deepcopy
from functools import reduce

from hocon.exceptions import HOCONExcessiveDataError
from hocon.parser._data import ParserInput
from hocon.parser._eat import eat_comments, eat_whitespace
from hocon.unresolved import (
    UnresolvedConcatenation,
    UnresolvedDuplication,
    UnresolvedSubstitution,
)


def merge_unconcatenated(
    unconcatenated_dictionary: dict,
    keys: list,
    unconcatenated_value: UnresolvedConcatenation | dict,
) -> dict:
    def set_default(dictionary: dict, key: str) -> dict:
        value = dictionary.get(key)
        new_element: dict = {}
        if isinstance(value, UnresolvedDuplication):
            value.append(new_element)
        elif value is not None:
            dictionary[key] = UnresolvedDuplication((value, new_element))
        else:
            dictionary[key] = new_element
        return new_element

    last_nest = reduce(set_default, keys[:-1], unconcatenated_dictionary)
    if isinstance(last_nest.get(keys[-1]), UnresolvedDuplication):
        last_nest[keys[-1]].append(unconcatenated_value)
    elif last_nest.get(keys[-1]) is not None:
        last_nest[keys[-1]] = UnresolvedDuplication((last_nest[keys[-1]], unconcatenated_value))
    else:
        last_nest[keys[-1]] = unconcatenated_value
    return deepcopy(unconcatenated_dictionary)


def convert_iadd_to_self_referential_substitution(
    keys: list[str],
    concatenation: UnresolvedConcatenation,
    current_keypath: list[str],
    root_location: list[str],
) -> UnresolvedConcatenation:
    """Turn this expression: a += 1 into this: a = ${?a} [1]."""
    return UnresolvedConcatenation(
        [
            UnresolvedSubstitution(
                keys,
                optional=True,
                relative_location=current_keypath,
                including_root=root_location,
            ),
            [concatenation],
        ],
    )


def assert_no_content_left(data: ParserInput, idx: int) -> None:
    try:
        while True:
            old_idx = idx
            idx = eat_whitespace(data, idx)
            idx = eat_comments(data, idx)
            if idx == old_idx:
                msg = "Excessive meaningful data outside of the HOCON structure."
                raise HOCONExcessiveDataError(msg, data, idx)
    except IndexError:
        pass
