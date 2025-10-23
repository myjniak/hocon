import pytest

import hocon
from hocon.exceptions import HOCONInvalidKeyError

pytestmark = pytest.mark.f11


def test_substitution_nesting():
    """You can't nest substitutions inside other substitutions"""
    data = """
    a = 1
    b = a
    c = ${${b}}
    """
    with pytest.raises(HOCONInvalidKeyError):
        hocon.loads(data)


def test_substitution_in_key():
    """You can't have substitutions in keys"""
    data = """
    a = a
    b = b
    c.${a} = c
    """
    with pytest.raises(HOCONInvalidKeyError):
        hocon.loads(data)


@pytest.mark.parametrize("key", [
    "a..b",
    ".a",
    "a.",
])
def test_bad_dot_placement(key: str):
    data = f"{key}: x"
    with pytest.raises(HOCONInvalidKeyError):
        hocon.loads(data)
