"""Unquoted string, as its initial characters do not parse as true, false, null, or a number."""
import hocon
import pytest


pytestmark = pytest.mark.f8


@pytest.mark.parametrize("data, expected", [
    ("[trueashell]", [True]),
    ("[falsefalse]", [False]),
    ("[nullisanull]", [None]),
    ("[1]", [1]),
    ("[-0.24]", [-0.24])
])
def test_other_types(data: str, expected: list):
    assert hocon.loads(data) == expected
