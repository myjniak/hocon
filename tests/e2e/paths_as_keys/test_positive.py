"""If a key is a path expression with multiple elements,
it is expanded to create an object for each path element other than the last.
The last path element, combined with the value, becomes a field in the most-nested object.
"""
import pytest

import hocon

pytestmark = pytest.mark.f12


@pytest.mark.parametrize("data, expected", [
    ("foo.bar : 42", {"foo": {"bar": 42}}),
    ("foo.bar.baz : 42", {"foo": {"bar": {"baz": 42}}}),
    ("a.x : 42, a.y : 43", {"a": {"x": 42, "y": 43}}),
    ("a b c : 42", {"a b c": 42}),
])
def test_dot_makes_nesting(data: str, expected: dict):
    assert hocon.loads(data) == expected


@pytest.mark.parametrize("data, expected", [
    ("true : 42", {"true": 42}),
    ("3 : 42", {"3": 42}),
    ("3.14 : 42", {"3": {"14": 42}}),
])
def test_path_are_always_string(data: str, expected: dict):
    assert hocon.loads(data) == expected
