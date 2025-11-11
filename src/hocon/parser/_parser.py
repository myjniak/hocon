from pathlib import Path
from typing import Any

from hocon.constants import ROOT_TYPE, UNDEFINED
from hocon.exceptions import (
    HOCONExcessiveDataError,
    HOCONIncludeError,
    HOCONNoDataError,
)
from hocon.unresolved import UnresolvedConcatenation

from ._data import ParserInput
from ._eat import (
    eat_comments,
    eat_dict_item_separators,
    eat_list_item_separators,
    eat_whitespace,
    eat_whitespace_and_comments,
)
from ._key import parse_keypath
from ._quoted_string import parse_quoted_string
from ._simple_value import parse_simple_value
from ._value_utils import (
    convert_iadd_to_self_referential_substitution,
    merge_unconcatenated,
)


def parse(data: str, root_filepath: str | Path | None = None, encoding: str = "UTF-8") -> ROOT_TYPE:
    root_filepath = root_filepath or Path.cwd()
    if not data:
        msg = "Empty string provided"
        raise HOCONNoDataError(msg)
    data_object = ParserInput(data, Path(root_filepath), encoding=encoding)
    result: ROOT_TYPE
    idx = eat_whitespace_and_comments(data_object, 0)
    if data[idx] == "[":
        result, idx = parse_list(data_object, idx=idx + 1)
    elif data[idx] == "{":
        result, idx = parse_dict(data_object, idx=idx + 1)
    else:
        data_object.data += "\n}"
        result, idx = parse_dict(data_object, idx=idx)
    _assert_no_content_left(data_object, idx)
    return result


def parse_dict(data: ParserInput, idx: int = 0, current_keypath: list[str] | None = None) -> tuple[dict, int]:
    if current_keypath is None:
        current_keypath = []
    unconcatenated_dictionary: dict = {}
    while True:
        idx = eat_whitespace_and_comments(data, idx)
        if data[idx] == "}":
            idx += 1
            break
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
                keypath.keys,
                unconcatenated_value,
                current_keypath=current_keypath + keypath.keys,
                root_location=data.root_path,
            )
        unconcatenated_dictionary = merge_unconcatenated(unconcatenated_dictionary, keypath.keys, unconcatenated_value)
    return unconcatenated_dictionary, idx


def parse_list(data: ParserInput, idx: int = 0, current_keypath: list[str] | None = None) -> tuple[list, int]:
    if current_keypath is None:
        current_keypath = []
    unconcatenated_list: list[UnresolvedConcatenation] = []
    index = 0
    while True:
        idx = eat_whitespace(data, idx)
        if data[idx] == "]":
            idx += 1
            return unconcatenated_list, idx
        unconcatenated_value, idx = parse_list_element(data, idx=idx, current_keypath=[*current_keypath, str(index)])
        unconcatenated_list.append(unconcatenated_value)
        index += 1


def parse_value_chunk(data: ParserInput, idx: int, current_keypath: list[str]) -> tuple[Any, int]:
    char = data[idx]
    if char == "{":
        dictionary, idx = parse_dict(data, idx=idx + 1, current_keypath=current_keypath)
        return dictionary, idx
    if char == "[":
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
    idx = eat_whitespace_and_comments(data, idx)
    if data[idx : idx + 3] == '"""' or data[idx] != '"':
        msg = "Only single quoted include filepaths are supported."
        raise HOCONIncludeError(msg)
    string, idx = parse_quoted_string(data, idx + 1)
    external_filepath = Path(data.absolute_filepath).parent / string
    try:
        with Path(external_filepath).open("r", encoding=data.encoding) as conf:
            external_file_content = conf.read()
    except FileNotFoundError:
        return UNDEFINED
    external_input = ParserInput(
        data=external_file_content,
        absolute_filepath=external_filepath,
        root_path=data.root_path + current_keypath,
    )
    ext_idx = eat_whitespace_and_comments(external_input, 0)
    if external_input[ext_idx] == "[":
        msg = "An included file must contain an object, not an array."
        raise HOCONIncludeError(msg)
    if external_input[ext_idx] == "{":
        external_dict, ext_idx = parse_dict(external_input, idx=ext_idx + 1, current_keypath=current_keypath)
    else:
        external_input.data += "\n}"
        external_dict, ext_idx = parse_dict(external_input, idx=ext_idx, current_keypath=current_keypath)
    _assert_no_content_left(external_input, ext_idx)
    return external_dict, idx


def _assert_no_content_left(data: ParserInput, idx: int) -> None:
    try:
        while True:
            old_idx = idx
            idx = eat_whitespace(data, idx)
            idx = eat_comments(data, idx)
            if idx == old_idx:
                msg = "Excessive meaningful data outside of the HOCON structure."
                raise HOCONExcessiveDataError(msg)
    except IndexError:
        return
