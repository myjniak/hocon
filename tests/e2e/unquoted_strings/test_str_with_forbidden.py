"""Tests unquoted string_ ending with forbidden characters"""
import json

import pytest

import hocon
from hocon.exceptions import (
    HOCONExcessiveDataError,
    HOCONUnexpectedBracesError,
    HOCONUnquotedStringError,
)

pytestmark = pytest.mark.f8


@pytest.mark.parametrize("forbidden", [
    "$", "[", "{", ":", "=", "+", "`", "^", "?", "!", "@", "*", "&", "\\",
])
def test_forbidden_chars_raise_exception(forbidden: str):
    with pytest.raises(HOCONUnquotedStringError):
        hocon.loads(f"[str with illegal char{forbidden}]")


@pytest.mark.parametrize("forbidden", [
    "#", "//",
])
def test_unclosed_list_brace_causes_parsing_out_of_range(forbidden: str):
    with pytest.raises(IndexError):
        hocon.loads(f"[str with illegal char{forbidden}]")


@pytest.mark.parametrize("forbidden", [
    '"',
])
def test_unclosed_double_quote_casues_decode_error(forbidden: str):
    with pytest.raises(json.decoder.JSONDecodeError):
        hocon.loads(f"[str with illegal char{forbidden}]")


@pytest.mark.parametrize("forbidden", [
    "}",
])
def test_closing_inexistent_dict(forbidden: str):
    with pytest.raises(HOCONUnexpectedBracesError):
        hocon.loads(f"[str with illegal char{forbidden}]")


@pytest.mark.parametrize("forbidden", [
    "]",
])
def test_excessive_list_closure(forbidden: str):
    with pytest.raises(HOCONExcessiveDataError):
        hocon.loads(f"[str with illegal char{forbidden}]")


@pytest.mark.parametrize("forbidden", [
    ",",
])
def test_list_with_trailing_comma(forbidden: str):
    """This will actually not result in an exception as trailing comma in lists are valid"""
    result = hocon.loads(f"[str with illegal char{forbidden}]")
    assert result == ["str with illegal char"]
