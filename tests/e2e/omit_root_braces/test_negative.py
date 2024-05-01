import hocon
import pytest

from hocon.exceptions import HOCONNoDataError, HOCONDecodeError, HOCONExcessiveDataError, HOCONUnexpectedBracesError

pytestmark = [pytest.mark.f3, pytest.mark.r1]


def test_empty():
    """Empty files are invalid documents"""
    with pytest.raises(HOCONNoDataError):
        hocon.loads("")


@pytest.mark.parametrize("data", [
    "15",
    "\"string_\"",
    "-Infinity",
    "null",
    "true"
])
def test_invalid_root(data):
    """files containing only a non-array non-object value such as a string_ are invalid HOCONs."""
    with pytest.raises(HOCONDecodeError):
        hocon.loads(data)


@pytest.mark.parametrize("data", [
    "key=value}",
    "[value]}",
    "[value]]"
])
def test_non_matching_braces(data):
    """A HOCON file is invalid if it omits the opening { but still has a closing }.
     The curly braces must be balanced."""
    with pytest.raises(HOCONExcessiveDataError):
        hocon.loads(data)


@pytest.mark.parametrize("data", [
    "key:value]",
])
def test_unexpected_braces(data):
    """A HOCON file is invalid if it omits the opening { but still has a closing }.
     The curly braces must be balanced."""
    with pytest.raises(HOCONUnexpectedBracesError):
        hocon.loads(data)
