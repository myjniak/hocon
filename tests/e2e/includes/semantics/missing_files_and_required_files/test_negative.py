from pathlib import Path

import pytest

import hocon
from hocon.exceptions import HOCONIncludeError

pytestmark = pytest.mark.f14_4


def test_required_no_opening_bracket():
    """When required syntax doesn't start with a '(' bracket."""
    conf_filepath = Path(__file__).parent / "data" / "required_no_opening.conf"
    with pytest.raises(HOCONIncludeError, match="\("):
        hocon.load(open(conf_filepath))


def test_required_no_closing_bracket():
    """When required syntax doesn't close with a ')' bracket."""
    conf_filepath = Path(__file__).parent / "data" / "required_no_closing.conf"
    with pytest.raises(HOCONIncludeError, match="\)"):
        hocon.load(open(conf_filepath))


def test_required_missing():
    """If however an included resource is mandatory then the name of the included resource
    may be wrapped with required(), in which case file parsing will fail with an error
    if the resource cannot be resolved."""
    conf_filepath = Path(__file__).parent / "data" / "required_missing.conf"
    with pytest.raises(FileNotFoundError):
        hocon.load(open(conf_filepath))
