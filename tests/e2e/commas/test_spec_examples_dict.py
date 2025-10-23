import pytest

import hocon
from hocon.exceptions import HOCONUnexpectedSeparatorError

pytestmark = pytest.mark.f5


def test_trailing_comma():
    result = hocon.loads("{k1:v1, k2:v2,}")
    assert result == {
        "k1": "v1",
        "k2": "v2",
    }


def test_newline_instead_of_comma():
    result = hocon.loads("{k1:v1\nk2:v2}")
    assert result == {
        "k1": "v1",
        "k2": "v2",
    }


def test_double_comma_in_the_end():
    with pytest.raises(HOCONUnexpectedSeparatorError):
        hocon.loads("{k1:v1,,}")


def test_leading_comma():
    with pytest.raises(HOCONUnexpectedSeparatorError):
        hocon.loads("{,k1:v1}")


def test_double_comma_in_the_middle():
    with pytest.raises(HOCONUnexpectedSeparatorError):
        hocon.loads("k1:v1,,k2:v2")
