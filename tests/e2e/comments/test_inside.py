from pathlib import Path

import pytest

from hocon import loads


pytestmark = pytest.mark.f2


def test_comment_inside_dict_values():
    data = (Path(__file__).parent / "data" / "inside_dict.hocon").read_text()
    result = loads(data)
    print(result)
    assert result == [
        {"k1": None, "k 2": 15, "k3": "val", "k4": "valu"},
        {"k1": "v1", "k2": "v2"}
    ]


def test_comment_inside_list():
    data = (Path(__file__).parent / "data" / "inside_list.hocon").read_text()
    result = loads(data)
    assert result == ["after: null", "after 215", "during", "_val", "during2 valu"]
