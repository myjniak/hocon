import pytest

import hocon

pytestmark = pytest.mark.f4


def test_regular_separator():
    """The = character can be used anywhere JSON allows :, i.e. to separate keys from values."""
    result = hocon.loads("{k:v, k2=v2, k 3 : v 3, k 4 = v 4}")
    assert result == {
        "k": "v",
        "k2": "v2",
        "k 3": "v 3",
        "k 4": "v 4",
    }


def test_no_separator():
    """If a key is followed by {, the : or = may be omitted. So "foo" {} means "foo" : {}"""
    result = hocon.loads("{a {b: {c {d: []}}}}")
    assert result == {
        "a": {
            "b": {
                "c": {
                    "d": [],
                },
            },
        },
    }
