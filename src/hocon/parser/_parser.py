from hocon.constants import ANY_VALUE_TYPE
from hocon.unresolved import UnresolvedConcatenation
from ._eat import eat_comments, eat_dict_item_separators, eat_whitespace, eat_list_item_separators
from ._key import parse_keypath
from ._simple_value import parse_simple_value
from ._value_utils import merge_unconcatenated


def parse_dict(data: str, idx: int = 0) -> tuple[dict, int]:
    unconcatenated_dictionary = {}
    while True:
        idx = eat_whitespace(data, idx)
        if data[idx] == "}":
            idx += 1
            return unconcatenated_dictionary, idx
        keys, idx = parse_keypath(data, idx=idx)
        unconcatenated_value, idx = parse_dict_value(data, idx=idx)
        unconcatenated_dictionary = merge_unconcatenated(unconcatenated_dictionary, keys, unconcatenated_value)


def parse_list(data: str, idx: int = 0) -> tuple[list, int]:
    unconcatenated_list = []
    while True:
        idx = eat_whitespace(data, idx)
        if data[idx] == "]":
            idx += 1
            return unconcatenated_list, idx
        unconcatenated_value, idx = parse_list_element(data, idx=idx)
        unconcatenated_list.append(unconcatenated_value)


def parse_value_chunk(data: str, idx: int = 0) -> tuple[ANY_VALUE_TYPE, int]:
    char = data[idx]
    if char == "{":
        dictionary, idx = parse_dict(data, idx=idx + 1)
        return dictionary, idx
    elif char == "[":
        list_, idx = parse_list(data, idx=idx + 1)
        return list_, idx
    return parse_simple_value(data, idx)


def parse_dict_value(data: str, idx: int) -> tuple[UnresolvedConcatenation, int]:
    values = UnresolvedConcatenation()
    while True:
        old_idx = idx
        idx = eat_comments(data, idx)
        if values and old_idx != idx:
            return values, idx
        value, idx = parse_value_chunk(data, idx=idx)
        values.append(value)
        separator_found, idx = eat_dict_item_separators(data, idx)
        if separator_found:
            return values, idx


def parse_list_element(data: str, idx: int) -> tuple[UnresolvedConcatenation, int]:
    values = UnresolvedConcatenation()
    while True:
        old_idx = idx
        idx = eat_comments(data, idx)
        if values and old_idx != idx:
            return values, idx
        value, idx = parse_value_chunk(data, idx=idx)
        values.append(value)
        separator_found, idx = eat_list_item_separators(data, idx)
        if separator_found:
            return values, idx
