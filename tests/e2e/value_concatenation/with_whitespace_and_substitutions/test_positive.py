"""When concatenating substitutions such as ${foo} ${bar},
the substitutions may turn out to be strings (which makes the whitespace between them significant)
or may turn out to be objects or lists (which makes it irrelevant).
Unquoted whitespace must be ignored in between substitutions which resolve to objects or lists.
"""

import pytest

import hocon

pytestmark = pytest.mark.f10_3


def test_subs_as_strings():
    """The substitutions may turn out to be strings (which makes the whitespace between them significant)"""
    data = """
    foo = "a"
    bar = "b"
    c = ${foo}  ${bar}
    """
    result = hocon.loads(data)
    assert result == {
        "foo": "a",
        "bar": "b",
        "c": "a  b"
    }


def test_subs_as_dicts():
    """The substitutions may turn out to be objects (which makes the whitespace between them irrelevant)"""
    data = """
        foo = {a: a}
        bar = {b: b}
        c = ${foo}  ${bar}
        """
    result = hocon.loads(data)
    assert result == {
        "foo": {"a": "a"},
        "bar": {"b": "b"},
        "c": {"a": "a", "b": "b"}
    }


def test_subs_as_lists():
    """The substitutions may turn out to be lists (which makes the whitespace between them irrelevant)"""
    data = """
        foo = [a]
        bar = [b]
        c = ${foo}  ${bar}
        """
    result = hocon.loads(data)
    assert result == {
        "foo": ["a"],
        "bar": ["b"],
        "c": ["a", "b"]
    }
