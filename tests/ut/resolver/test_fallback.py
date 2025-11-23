import pytest

from hocon.exceptions import HOCONSubstitutionUndefinedError
from hocon.parser import parse
from hocon.resolver import resolve, _lazy_resolver
from hocon.resolver._self_reference import cut_self_reference_and_fields_that_override_it
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
        b: c${a.a}d
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


def test_array_ref():
    """cutting self reference should work on parsed object with reference to array index."""
    data = """
    a: [
        1,
        2,
        {b: [1, 2, ${a.0}, 4]},
        4
    ]
    """
    parsed = parse(data)
    sub = parsed["a"][0][2][0]["b"][0][2][0]
    carved = cut_self_reference_and_fields_that_override_it(sub, parsed)
    result = resolve(carved)
    assert result == {"a": [1, 2, {"b": [1, 2, 4]}, 4]}


def test_array_ref2():
    """cutting self reference should also work on lazy-resolved object."""
    data = """
    a: [
        1,
        2,
        {b: [1, 2, ${a.0}, 4]},
        4
    ]
    """
    parsed = parse(data)
    lazy_resolved = _lazy_resolver.resolve(parsed)
    sub = lazy_resolved["a"][2]["b"][2]
    carved = cut_self_reference_and_fields_that_override_it(sub, lazy_resolved)
    result = resolve(carved)
    assert result == {"a": [1, 2, {"b": [1, 2, 4]}, 4]}


def test_wrong_location():
    """When given substitution is deeper than expected.
    Honestly, I don't know how to naturally trigger this exception.
    In this test, substituion at location a.c is moved deeper to a.c.0."""
    data = """
    a.c: ${?a.b} "42"
    a {b: 1}
    """
    parsed = parse(data)
    sub: UnresolvedSubstitution = parsed["a"][0]["c"][0]
    parsed["a"][0]["c"] = [sub, "42"]
    with pytest.raises(HOCONSubstitutionUndefinedError):
        cut_self_reference_and_fields_that_override_it(sub, parsed)
