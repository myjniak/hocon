"""substitutions normally "look forward" and use the final value for their path expression
when this would create a cycle, when possible the cycle must be broken by looking backward only
(thus removing one of the substitutions that's a link in the cycle)
"""

import pytest

import hocon

pytestmark = pytest.mark.f13_1


def test_basic():
    data = """
    path : "a:b:c"
    path : ${path}":d"
    """
    result = hocon.loads(data)
    assert result == {
        "path": "a:b:c:d",
    }


@pytest.mark.parametrize("data, expected", [
    ("a : a, a : ${a}", {"a": "a"}),
    ("a : a, a : ${a}bc", {"a": "abc"}),
    ("path : [/etc], path : ${path} [ /usr/bin ]", {"path": ["/etc", "/usr/bin"]}),
])
def test_examples(data: str, expected: dict):
    assert hocon.loads(data) == expected


def test_breakable_cycle():
    data = """a={ x : 42, y : ${a.x} }"""
    result = hocon.loads(data)
    assert result == {
        "a": {
            "x": 42,
            "y": 42,
        },
    }
