import pytest
from hocon.exceptions import HOCONUnexpectedSeparatorError
import hocon

pytestmark = pytest.mark.f5


def test_trailing_comma():
    """[1,2,3,] and [1,2,3] are the same array."""
    result = hocon.loads("[1,2,3,]")
    result_2 = hocon.loads("[1,2,3]")
    assert result == result_2 == [1, 2, 3]


def test_newline_instead_of_comma():
    """[1\n2\n3] and [1,2,3] are the same array."""
    result = hocon.loads("[1\n2\n3]")
    result_2 = hocon.loads("[1,2,3]")
    assert result == result_2 == [1, 2, 3]


def test_double_comma_in_the_end():
    """[1,2,3,,] is invalid because it has two trailing commas."""
    with pytest.raises(HOCONUnexpectedSeparatorError):
        hocon.loads("[1,2,3,,]")


def test_leading_comma():
    """[,1,2,3] is invalid because it has an initial comma."""
    with pytest.raises(HOCONUnexpectedSeparatorError):
        hocon.loads("[,1,2,3]")


def test_double_comma_in_the_middle():
    """[1,,2,3] is invalid because it has two commas in a row."""
    with pytest.raises(HOCONUnexpectedSeparatorError):
        hocon.loads("[1,,2,3]")
