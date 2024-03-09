from functools import reduce

from ._eat import eat_comments, eat_whitespace_and_comments, eat_dict_item_separators, eat_whitespace, \
    eat_list_item_separators
from ._key import parse_keypath
from ._simple_value import parse_simple_value
from .constants import ANY_VALUE_TYPE
from .exceptions import HOCONNoDataError, HOCONDecodeError, HOCONExcessiveDataError


def loads(data: str) -> list | dict:
    if not data:
        raise HOCONNoDataError("Empty string provided")
    idx = eat_whitespace_and_comments(data, 0)
    if data[idx] == "[":
        result, idx = parse_list(data, idx=idx + 1)
    elif data[idx] == "{":
        result, idx = parse_dict(data, idx=idx + 1)
    else:
        data += "\n}"
        result, idx = parse_dict(data, idx=idx)
    assert_no_content_left(data, idx)
    return result


def assert_no_content_left(data: str, idx: int) -> None:
    try:
        while True:
            old_idx = idx
            idx = eat_whitespace(data, idx)
            idx = eat_comments(data, idx)
            if idx == old_idx:
                raise HOCONExcessiveDataError("Excessive meaningful data outside of the HOCON structure.")
    except IndexError:
        return


def parse_value_chunk(data: str, idx: int = 0) -> tuple[ANY_VALUE_TYPE, int, bool]:
    char = data[idx]
    if char == "{":
        dictionary, idx = parse_dict(data, idx=idx + 1)
        return dictionary, idx, False
    elif char == "[":
        list_, idx = parse_list(data, idx=idx + 1)
        return list_, idx, False
    return parse_simple_value(data, idx)


def concatenate(values: list[ANY_VALUE_TYPE]) -> ANY_VALUE_TYPE:
    if not values:
        raise HOCONDecodeError("Expected value not found")
    if all(isinstance(value, list) for value in values):
        return sum(values, [])
    if all(isinstance(value, dict) for value in values):
        return reduce(merge, values)
    if all(isinstance(value, str) for value in values):
        return "".join(values)
    if len(values) == 1:
        return values[0]
    raise HOCONDecodeError("Multiple types concatenation not supported")


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


def evaluate_path_value(keys: list[str], value) -> ANY_VALUE_TYPE:
    if len(keys) == 1:
        return value
    dictionary = {keys[-1]: value}
    for key in reversed(keys[1:-1]):
        dictionary = {key: dictionary}
    return dictionary


def merge(dictionary: dict, superior_dict: dict[str, ANY_VALUE_TYPE]) -> dict:
    """If both values are objects, then the objects are merged."""
    for key, value in superior_dict.items():
        if isinstance(value, dict) and isinstance(dictionary.get(key), dict):
            dictionary[key] = merge(dictionary[key], value)
        else:
            dictionary[key] = value
    return dictionary


def parse_dict(data: str, idx: int = 0) -> tuple[dict, int]:
    dictionary = {}
    while True:
        idx = eat_whitespace(data, idx)
        if data[idx] == "}":
            idx += 1
            break
        keys, idx = parse_keypath(data, idx=idx)
        value, idx = parse_dict_value(data, idx=idx)
        value = evaluate_path_value(keys, value)
        key = keys[0]
        dictionary = merge(dictionary, {key: value})

    return dictionary, idx


def parse_list(data: str, idx: int = 0) -> tuple[list, int]:
    values = []
    while True:
        idx = eat_whitespace(data, idx)
        if data[idx] == "]":
            idx += 1
            break
        value, idx = parse_list_element(data, idx=idx)
        values.append(value)
        x, idx = eat_list_item_separators(data, idx)
    return values, idx

# if __name__ == '__main__':
#     match = re.match(NUMBER_RE, "192.168.201.2/32")
#     print(match)
