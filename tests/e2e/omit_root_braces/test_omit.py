import hocon
import pytest


pytestmark = pytest.mark.f3


def test_omit_curly():
    """In HOCON, if the file does not begin with a square bracket or curly brace,
    it is parsed as if it were enclosed with {} curly braces."""
    result = hocon.loads("key=value")
    assert result == {"key": "value"}
