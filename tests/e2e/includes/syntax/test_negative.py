from pathlib import Path

import pytest

import hocon
from hocon.exceptions import HOCONIncludeError

pytestmark = pytest.mark.f14_1


def test_triple_quote():
    """If an unquoted include at the start of a key is followed by anything other than a single quoted string or
    the url("")/file("")/classpath("") syntax, it is invalid and an error should be generated.
    """
    conf_filepath = Path(__file__).parent / "data" / "bad_value" / "application.conf"
    with pytest.raises(HOCONIncludeError):
        hocon.load(open(conf_filepath))


def test_unquoted():
    """Value concatenation is NOT performed on the "argument" to include or url() etc.
    The argument must be a single quoted string.
    """
    conf_filepath = Path(__file__).parent / "data" / "bad_value" / "unquoted.conf"
    with pytest.raises(HOCONIncludeError):
        hocon.load(open(conf_filepath))


def test_sub():
    """[...] No substitutions are allowed, and the argument may not be an unquoted string or any other kind of value."""
    conf_filepath = Path(__file__).parent / "data" / "bad_value" / "sub.conf"
    with pytest.raises(HOCONIncludeError):
        hocon.load(open(conf_filepath))


def test_unquoted_include_but_later_in_keypath():
    """Unquoted include has no special meaning if it is not the start of a key's path expression."""
    result = hocon.loads("{ foo include : 42 }")
    assert result == {"foo include": 42}


def test_include_as_object_value():
    data = """
    { foo : include } # value is the string "include"
    """
    result = hocon.loads(data)
    assert result == {
        "foo": "include",
    }


def test_include_as_array_elem():
    data = """
    [ include ]       # array of one string "include"
    """
    result = hocon.loads(data)
    assert result == ["include"]


def test_include_quoted():
    """You can quote "include" if you want a key that starts with the word "include", only unquoted include is special"""
    data = """{ "include" : 42 }"""
    result = hocon.loads(data)
    assert result == {"include": 42}
