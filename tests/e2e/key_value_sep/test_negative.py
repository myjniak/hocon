import pytest

import hocon
from hocon.exceptions import HOCONInvalidKeyError


def test_no_separator():
    """A proper exception should be raised if key-value separator is not found."""
    data = """
    a = 1
    b   2
    """
    with pytest.raises(HOCONInvalidKeyError):
        hocon.loads(data)


def test_no_separator_2():
    """A proper exception should be raised if invalid character happens before key-value separator is found."""
    data = "{a = 1, b   2} :5"
    with pytest.raises(HOCONInvalidKeyError):
        hocon.loads(data)
