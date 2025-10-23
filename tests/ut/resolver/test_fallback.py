import pytest

from hocon._main import parse
from hocon.resolver._resolver import resolve
from hocon.resolver._self_reference import (
    cut_self_reference_and_fields_that_override_it,
)
from hocon.unresolved import UnresolvedConcatenation, UnresolvedSubstitution

pytestmark = pytest.mark.f13


def test_1():
    data = """
    a : { a : { c : 1 } }
    b : 1
    a : ${a.a}
    a : { a : 2 }
    b : 3
    """
    parsed = parse(data)
    sub = parsed["a"][1][0]
    carved = cut_self_reference_and_fields_that_override_it(sub, parsed)
    result = resolve(carved)
    assert result == {"a": {"a": {"c": 1}}, "b": 3}


def test_2():
    data = """
    a: [1, 2]
    a: ${a}[3, 4]
    """
    parsed = parse(data)
    sub = parsed["a"][1][0]
    carved = cut_self_reference_and_fields_that_override_it(sub, parsed)
    result = resolve(carved)
    assert result == {"a": [1, 2]}


def test_3():
    sub = UnresolvedSubstitution(["a"], optional=False, relative_location=["a"])
    parsed = {"a": UnresolvedConcatenation([sub])}
    result = cut_self_reference_and_fields_that_override_it(sub, parsed)
    assert resolve(result) == {}


def test_4():
    data = """
    a {
        a: 1
        b: c${a.a}
    }
    """
    parsed = parse(data)
    sub = parsed["a"][0]["b"][1]
    carved = cut_self_reference_and_fields_that_override_it(sub, parsed)
    result = resolve(carved)
    assert result == {"a": {"a": 1, "b": "c"}}


def test_5():
    data = """
    a.c: ${?a.b} "42"
    a {b: 1}
    """
    parsed = parse(data)
    sub = parsed["a"][0]["c"][0]
    carved = cut_self_reference_and_fields_that_override_it(sub, parsed)
    result = resolve(carved)
    assert result == {"a": {"b": 1}}
