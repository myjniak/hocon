"""
Quoted whitespace between substitutions that resolve to list/dict should be an error.
"""

import pytest

import hocon
from hocon.exceptions import HOCONConcatenationError

pytestmark = pytest.mark.f10_3


def test_quoted_whitespace_between_dicts():
    data = """
        foo = {a: a}
        bar = {b: b}
        c = ${foo}"  "${bar}
        """
    with pytest.raises(HOCONConcatenationError, match="dict"):
        hocon.loads(data)


def test_quoted_whitespace_between_lists():
    data = """
        foo = [a]
        bar = [b]
        c = ${foo}"  "${bar}
        """
    with pytest.raises(HOCONConcatenationError, match="list"):
        hocon.loads(data)
