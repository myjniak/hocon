import pytest

import hocon
from hocon.exceptions import HOCONConcatenationError

pytestmark = pytest.mark.f10_1


def test_list_in_string_concatenation():
    """It is invalid for arrays to appear in a string_ value concatenation."""
    with pytest.raises(HOCONConcatenationError):
        hocon.loads("[concatenate a [list]]")


def test_dict_in_string_concatenation():
    """It is invalid for objects to appear in a string_ value concatenation."""
    with pytest.raises(HOCONConcatenationError):
        hocon.loads("[concatenate a {di:ct}]")
