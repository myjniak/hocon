
import pytest

import hocon

pytestmark = pytest.mark.f11


def test_dot_as_path_separator():
    """Any . characters outside quoted strings are understood as path separators,
    while inside quoted strings . has no special meaning."""
    data = """
    foo.bar."hello.world" = x
    """
    result = hocon.loads(data)
    assert result == {
        "foo": {
            "bar": {
                "hello.world": "x"
            }
        }
    }


@pytest.mark.parametrize("key, expected", [
    ("10.0foo", {"10": {"0foo": "x"}}),
    ("foo10.0", {"foo10": {"0": "x"}}),
    ('foo"10.0"', {"foo10.0": "x"}),
    ("1.2.3", {"1": {"2": {"3": "x"}}})
])
def test_dot_in_float_counts_as_path_separator(key: str, expected: dict):
    data = f"{key}: x"
    result = hocon.loads(data)
    assert result == expected


def test_keypath_is_always_string():
    """If you have a path expression (in a key or substitution) then it must always be converted to a string."""
    data = f"true.null.0 = x"
    result = hocon.loads(data)
    assert result == {
        "true": {
            "null": {
                "0": "x"
            }
        }
    }


@pytest.mark.parametrize("data, expected", [
    ('"": x', {"": "x"}),
    ('a."".b = x', {"a": {"": {"b": "x"}}})
])
def test_keypath_as_empty_string(data: str, expected: dict):
    result = hocon.loads(data)
    assert result == expected
