from pathlib import Path

import pytest

from hocon import loads

pytestmark = pytest.mark.f2


def test_comment_before_hocon():
    data = (Path(__file__).parent / "data" / "before.hocon").read_text()
    result = loads(data)
    assert result == {"key": "value"}


def test_comment_after_hocon():
    data = (Path(__file__).parent / "data" / "after.hocon").read_text()
    result = loads(data)
    assert result == {"key": "value"}


def test_comment_after_hocon_2():
    data = (Path(__file__).parent / "data" / "after2.hocon").read_text()
    result = loads(data)
    assert result == {"key": {"nested": "value"}}
