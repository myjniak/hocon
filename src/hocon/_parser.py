from ._eat import eat_comments, eat_dict_item_separators, eat_whitespace, eat_list_item_separators
from ._key import parse_keypath
from ._simple_value import parse_simple_value
from ._value_utils import concatenate, merge, evaluate_path_value
from .constants import ANY_VALUE_TYPE


def parse_dict(data: str, idx: int = 0) -> tuple[dict, int]:
    dictionary = {}
    while True:
        idx = eat_whitespace(data, idx)
        if data[idx] == "}":
            idx += 1
            return dictionary, idx
        keys, idx = parse_keypath(data, idx=idx)
        value, idx = parse_dict_value(data, idx=idx)
        value = evaluate_path_value(keys, value)
        key = keys[0]
        dictionary = merge(dictionary, {key: value})


def parse_list(data: str, idx: int = 0) -> tuple[list, int]:
    values = []
    while True:
        idx = eat_whitespace(data, idx)
        if data[idx] == "]":
            idx += 1
            return values, idx
        value, idx = parse_list_element(data, idx=idx)
        values.append(value)


def parse_value_chunk(data: str, idx: int = 0) -> tuple[ANY_VALUE_TYPE, int, bool]:
    char = data[idx]
    if char == "{":
        dictionary, idx = parse_dict(data, idx=idx + 1)
        return dictionary, idx, False
    elif char == "[":
        list_, idx = parse_list(data, idx=idx + 1)
        return list_, idx, False
    return parse_simple_value(data, idx)


def parse_dict_value(data: str, idx: int) -> tuple[ANY_VALUE_TYPE, int]:
    values = []
    while True:
        idx = eat_comments(data, idx)
        value, idx, is_last_chunk = parse_value_chunk(data, idx=idx)
        values.append(value)
        separator_found, idx = eat_dict_item_separators(data, idx)
        if separator_found or is_last_chunk:
            return concatenate(values), idx


def parse_list_element(data: str, idx: int) -> tuple[ANY_VALUE_TYPE, int]:
    values = []
    while True:
        idx = eat_comments(data, idx)
        value, idx, is_last_chunk = parse_value_chunk(data, idx=idx)
        values.append(value)
        separator_found, idx = eat_list_item_separators(data, idx)
        if separator_found or is_last_chunk:
            return concatenate(values), idx
