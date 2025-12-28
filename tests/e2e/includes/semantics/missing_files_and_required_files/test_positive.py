from pathlib import Path

import pytest

import hocon

pytestmark = pytest.mark.f14_4


def test_missing():
    """By default, if an included file does not exist then the include statement should be silently ignored
    (as if the included file contained only an empty object).
    """
    conf_filepath = Path(__file__).parent / "data" / "missing.conf"
    result = hocon.load(open(conf_filepath))
    assert result == {"a": 1, "c": 3}


def test_required():
    """If however an included resource is mandatory then the name of the included resource
    may be wrapped with required().
    """
    conf_filepath = Path(__file__).parent / "data" / "required.conf"
    result = hocon.load(open(conf_filepath))
    assert result == {"a": 1, "b": 2, "c": 3}


def test_file():
    conf_filepath = Path(__file__).parent / "data" / "file.conf"
    result = hocon.load(open(conf_filepath))
    assert result == {"a": 1, "b": 2, "c": 3, "d": 4}
