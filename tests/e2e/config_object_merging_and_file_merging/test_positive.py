import pytest

from hocon.resolver import merge

pytestmark = pytest.mark.f21


def test_non_object_value_hides_earlier():
    """As with duplicate keys, an intermediate non-object value "hides" earlier object values."""
    a = { "a" : { "x" : 1 } }
    b = { "a" : 42 }
    c = { "a" : { "y" : 2 } }
    result = merge(a, merge(b, c))
    assert result == {"a": {"x": 1}}


def test_inferior_object_value_ignored():
    """This rule for merging objects loaded from different
    files is exactly the same behavior as for merging duplicate fields in the same file.
    All merging works the same way."""
    a = { "a" : { "x" : 1 } }
    b = {"a": {"y": 2}}
    c = { "a" : 42 }
    result = merge(a, merge(b, c))
    assert result == {"a": {"x": 1, "y": 2}}
