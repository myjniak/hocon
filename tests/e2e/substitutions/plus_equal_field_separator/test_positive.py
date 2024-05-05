"""Fields may have += as a separator rather than : or =.
A field with += transforms into a self-referential array concatenation."""

import pytest

import hocon

pytestmark = pytest.mark.f13_2


@pytest.mark.xfail
def test_iadd():
    data = """
    a = [1, 2]
    a += 3
    """
    result = hocon.loads(data)
    assert result == {
        "a": [1, 2, 3]
    }


@pytest.mark.xfail
def test_iadd_no_previous_value():
    data = """
    a += 3
    """
    result = hocon.loads(data)
    assert result == {
        "a": [3]
    }
