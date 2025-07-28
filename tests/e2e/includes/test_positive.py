from pathlib import Path

import pytest

import hocon

pytestmark = pytest.mark.f14_1


def test_basic():
    """An include statement can appear in place of an object field."""
    conf_filepath = Path(__file__).parent / "data" / "basic" / "application.conf"
    result = hocon.load(open(conf_filepath))
    assert result == {"a": {"a": 1}}


def test_lots_of_space_between_include_and_resource_name():
    """There can be any amount of whitespace, including newlines, between the unquoted include and the resource name."""
    conf_filepath = Path(__file__).parent / "data" / "lots_of_space" / "application.conf"
    result = hocon.load(open(conf_filepath))
    assert result == {"a": {"a": 1}}
