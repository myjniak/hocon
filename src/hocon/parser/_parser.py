from pathlib import Path
from typing import Any, Optional

from ._data import ParserInput
from ._eat import eat_comments, eat_dict_item_separators, eat_whitespace, eat_list_item_separators
from ._key import parse_keypath
from ._quoted_string import parse_quoted_string
from ._simple_value import parse_simple_value
from ._value_utils import merge_unconcatenated, convert_iadd_to_self_referential_substitution
from ..constants import UNDEFINED
from ..exceptions import HOCONIncludeError
from ..unresolved import UnresolvedConcatenation, UnresolvedSubstitution


def parse_dict(data: ParserInput, idx: int = 0, current_keypath: Optional[list[str]] = None) -> tuple[dict, int]:
    if current_keypath is None:
        current_keypath = []
    unconcatenated_dictionary: dict = {}
    while True:
        idx = eat_whitespace(data, idx)
        if data[idx] == "}":
            idx += 1
            return unconcatenated_dictionary, idx
        keypath = parse_keypath(data, idx=idx)
        if keypath.include:
            ext_dict, idx = parse_include(data, idx=keypath.end_idx, current_keypath=current_keypath)
            for ext_key, ext_value in ext_dict.items():
                unconcatenated_dictionary = merge_unconcatenated(unconcatenated_dictionary, [ext_key], ext_value)
            continue
        idx = eat_whitespace(data, keypath.end_idx)
        unconcatenated_value, idx = parse_dict_value(data, idx=idx, current_keypath=current_keypath + keypath.keys)
        if keypath.iadd:
            unconcatenated_value = convert_iadd_to_self_referential_substitution(
                keypath.keys, unconcatenated_value, current_keypath=current_keypath + keypath.keys
            )
        unconcatenated_dictionary = merge_unconcatenated(unconcatenated_dictionary, keypath.keys, unconcatenated_value)


def parse_list(data: ParserInput, idx: int = 0, current_keypath: Optional[list[str]] = None) -> tuple[list, int]:
    if current_keypath is None:
        current_keypath = []
    unconcatenated_list: list[UnresolvedConcatenation] = []
    index = 0
    while True:
        idx = eat_whitespace(data, idx)
        if data[idx] == "]":
            idx += 1
            return unconcatenated_list, idx
        unconcatenated_value, idx = parse_list_element(data, idx=idx, current_keypath=current_keypath + [str(index)])
        unconcatenated_list.append(unconcatenated_value)


def parse_value_chunk(data: ParserInput, idx: int, current_keypath: list[str]) -> tuple[Any, int]:
    char = data[idx]
    if char == "{":
        dictionary, idx = parse_dict(data, idx=idx + 1, current_keypath=current_keypath)
        return dictionary, idx
    elif char == "[":
        list_, idx = parse_list(data, idx=idx + 1, current_keypath=current_keypath)
        return list_, idx
    return parse_simple_value(data, idx, current_keypath=current_keypath)


def parse_dict_value(data: ParserInput, idx: int, current_keypath: list[str]) -> tuple[UnresolvedConcatenation, int]:
    values = UnresolvedConcatenation()
    while True:
        old_idx = idx
        idx = eat_comments(data, idx)
        if values and old_idx != idx:
            return values, idx
        value, idx = parse_value_chunk(data, idx, current_keypath=current_keypath)
        values.append(value)
        separator_found, idx = eat_dict_item_separators(data, idx)
        if separator_found:
            return values, idx


def parse_list_element(data: ParserInput, idx: int, current_keypath: list[str]) -> tuple[UnresolvedConcatenation, int]:
    values = UnresolvedConcatenation()
    while True:
        old_idx = idx
        idx = eat_comments(data, idx)
        if values and old_idx != idx:
            return values, idx
        value, idx = parse_value_chunk(data, idx, current_keypath=current_keypath)
        values.append(value)
        separator_found, idx = eat_list_item_separators(data, idx)
        if separator_found:
            return values, idx


def parse_include(data: ParserInput, idx: int, current_keypath: list[str]) -> tuple[dict, int]:
    """We start parsing right after 'include' phrase here."""
    if data[idx] == '"':
        string, idx = parse_quoted_string(data, idx + 1)
    else:
        raise HOCONIncludeError("Only single quoted include filepaths are currently supported.")
    external_filepath = Path(data.absolute_filepath).parent / string
    try:
        with open(external_filepath) as conf:
            external_file_content = conf.read()
    except FileNotFoundError:
        return UNDEFINED
    external_input = ParserInput(data=external_file_content, absolute_filepath=external_filepath)
    if external_input[0] == "{":
        external_dict, _ = parse_dict(external_input, idx=1, current_keypath=current_keypath)
    else:
        external_input.data += "\n}"
        external_dict, _ = parse_dict(external_input, idx=0, current_keypath=current_keypath)
    return external_dict, idx
