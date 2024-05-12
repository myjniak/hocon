from hocon._main import parse, resolve
from hocon.resolver._utils import cut_self_reference_and_fields_that_override_it
from hocon.unresolved import UnresolvedSubstitution, UnresolvedConcatenation


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
    assert result == {'a': {'a': {'c': 1}}, 'b': 3}


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
    sub = UnresolvedSubstitution(["a"], optional=False, location=["a"])
    parsed = {"a": UnresolvedConcatenation([sub])}
    result = cut_self_reference_and_fields_that_override_it(sub, parsed)
    assert resolve(result) == {}


def test_4():
    data = """
    a: {a: 1, b: 2}
    a: {a: 3, b: { c: ${a.a}, d: 4} {c: 6}}
    a: {a: 5, b: {c: 7}}
    """
    sub = UnresolvedSubstitution(["a", "a"], optional=False, location=["a", "b", "c"])
    parsed = parse(data)
    result = cut_self_reference_and_fields_that_override_it(sub, parsed)
    assert resolve(result) == {
        "a": {
            "a": 1, "b": 2
        }
    }
