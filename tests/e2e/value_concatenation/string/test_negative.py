import hocon
import pytest

from hocon.exceptions import HOCONUnquotedStringError

pytestmark = pytest.mark.f10_1


def test_list_in_string_concatenation():
    """it is invalid for arrays to appear in a string value concatenation."""
    with pytest.raises(HOCONUnquotedStringError):
        hocon.loads("[concatenate a [list]")


def test_dict_in_string_concatenation():
    """it is invalid for objects to appear in a string value concatenation."""
    with pytest.raises(HOCONUnquotedStringError):
        hocon.loads("[concatenate a {di:ct}")
