from functools import reduce
from itertools import chain

from ._key import parse_keypath
from ._simple_value import parse_simple_value
from .constants import WHITE_CHARS, ELEMENT_SEPARATORS, ANY_VALUE_TYPE, INLINE_WHITE_CHARS


class HOCONDecodeError(Exception):
    ...


class HoconNoDataError(HOCONDecodeError):
    """In case there is no data"""


class HoconBracesMismatchError(HOCONDecodeError):
    ...


def loads(data: str) -> list | dict:
    if not data:
        raise HoconNoDataError("Empty string provided")
    if data.startswith("["):
        return parse_list(data, idx=1)[0]
    elif data.startswith("{"):
        return parse_dict(data, idx=1)[0]
    else:
        return parse_dict(data + "}", idx=0)[0]


def eat_inline_whitespace(data: str, idx: int) -> int:
    while True:
        char = data[idx]
        if char not in INLINE_WHITE_CHARS:
            return idx
        idx += 1


def eat_whitespace(data: str, idx: int) -> int:
    while True:
        char = data[idx]
        if char not in WHITE_CHARS:
            return idx
        idx += 1


def eat_element_separators(data: str, idx: int) -> tuple[bool, int]:
    chars_to_eat = WHITE_CHARS + ELEMENT_SEPARATORS
    separator_found = False
    while True:
        char = data[idx]
        if char in "}]":
            return True, idx
        if char not in chars_to_eat:
            return separator_found, idx
        if char in ELEMENT_SEPARATORS:
            separator_found = True
        idx += 1


def parse_value_chunk(data: str, idx: int = 0) -> tuple[ANY_VALUE_TYPE, int]:
    char = data[idx]
    if char == "{":
        return parse_dict(data, idx=idx + 1)
    elif char == "[":
        return parse_list(data, idx=idx + 1)
    return parse_simple_value(data, idx)


def concatenate(values: list[ANY_VALUE_TYPE]) -> ANY_VALUE_TYPE:
    if all(isinstance(value, list) for value in values):
        return sum(values, [])
    if all(isinstance(value, dict) for value in values):
        return reduce(merge, values)
    if all(isinstance(value, str) for value in values):
        return "".join(values)
    if len(values) == 1:
        return values[0]
    raise HOCONDecodeError("Multiple types concatenation not supported")


def parse_value(data: str, idx: int) -> tuple[ANY_VALUE_TYPE, int]:
    values = []
    while True:
        value, idx = parse_value_chunk(data, idx=idx)
        values.append(value)
        separator_found, idx = eat_element_separators(data, idx)
        if separator_found:
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
        if data[idx] == "}":
            idx += 1
            break
        idx = eat_whitespace(data, idx)
        keys, idx = parse_keypath(data, idx=idx)
        value, idx = parse_value(data, idx=idx)
        value = evaluate_path_value(keys, value)
        key = keys[0]
        dictionary = merge(dictionary, {key: value})

    return dictionary, idx


def parse_list(data: str, idx: int = 0) -> tuple[list, int]:
    values = []
    while True:
        if data[idx] == "]":
            idx += 1
            break
        idx = eat_whitespace(data, idx)
        value, idx = parse_value_chunk(data, idx=idx)
        values.append(value)
        x, idx = eat_element_separators(data, idx)
    return values, idx

# if __name__ == '__main__':
#     match = re.match(NUMBER_RE, "192.168.201.2/32")
#     print(match)
