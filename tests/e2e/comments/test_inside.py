from pathlib import Path

import pytest

from hocon import loads

pytestmark = pytest.mark.f2


def test_comment_inside_dict_values():
    data = (Path(__file__).parent / "data" / "inside_dict.hocon").read_text()
    result = loads(data)
    assert result == [
        {"k1": None, "k 2": 15, "k3": "val", "k4": "valu"},
        {"k1": "v1", "k2": "v2"},
    ]


def test_comment_inside_list():
    data = (Path(__file__).parent / "data" / "inside_list.hocon").read_text()
    result = loads(data)
    assert result == ["v 1", "v 215", "v3", "_v4", "v5 and"]


def test_comment_after_values():
    data = """
    a: 55  // int
    b: 55.5 // float
    c: null // null
    d: true # bool
    e: ${c} // substitution
    f: [] # list
    g: {} # dict
    """
    result = loads(data)
    assert result == {
        "a": 55,
        "b": 55.5,
        "c": None,
        "d": True,
        "e": None,
        "f": [],
        "g": {},
    }
