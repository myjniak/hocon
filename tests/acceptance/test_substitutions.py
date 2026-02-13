from hocon import loads
from hocon.resolver import resolve
from hocon.parser import parse


def test_1():
    data = """
    d = {e: 1, f.g: [3, {4: 4, 99: ${x}}, 6]}      ,
    d = {e: 2}
    a = ${d.f.g}
    x = ${d.e}
    """
    result = loads(data)
    assert result == {
        "d": {
            "e": 2,
            "f": {
                "g": [3, {"4": 4, "99": 2}, 6],
            },
        },
        "a": [3, {"4": 4, "99": 2}, 6],
        "x": 2}


def test_2():
    data = """
    a: ${b} 
    b: 3 
    """
    result = loads(data)
    assert result == {
        "a": 3,
        "b": 3,
    }


def test_3():
    data = """
            a = {a: 1} {b:${a.a}} {c:3}
            """
    parsed = parse(data)
    resolved = resolve(parsed)
    assert resolved == {
        "a": {"a": 1, "b": 1, "c": 3},
    }


def test_4():
    data = """
            a = {a: 1} {b:hi ${a.a} mom} {c:3}
            a: {a: 4} {b: 5} {c: 6}
            """
    result = loads(data)
    expected = {
        "a": {
            "a": 4,
            "b": 5,
            "c": 6,
        },
    }
    assert result == expected


def test_5():
    data = """
            a: {a: 1} {b: ${x}} {c: ${x}}
            a: {b: 2} {c: 3}
            """
    result = loads(data)
    expected = {
        "a": {
            "a": 1,
            "b": 2,
            "c": 3,
        },
    }
    assert result == expected


def test_6():
    data = """
            a : [ 1, 2 ]
            a : ${a} [ 3, 4 ]
            """
    result = loads(data)
    assert result == {
        "a": [1, 2, 3, 4],
    }


def test_7():
    data = """
        a: 1
        b: c${a}
    """
    result = loads(data)
    assert result == {
        "a": 1,
        "b": "c1",
    }


def test_8():
    data = """
    a {
        a: 1
        b: c${a.a}
    }
    """
    result = loads(data)
    assert result == {
        "a": {
            "a": 1,
            "b": "c1",
        },
    }


def test_9():
    data = """
    a.c: ${?a.b} "42"
    a {b: 1}
    """
    assert loads(data) == {
        "a": {
            "b": 1,
            "c": "1 42",
        },
    }


def test_concatenation_with_undefined_subs():
    data = """url: "https://"${?predomain}google"."com"""
    assert loads(data) == {
        "url": "https://google.com",
    }


def test_substitution_with_array_in_path():
    data = """
    a: [1, 2, 3, 4]
    b: ${a.2}
    """
    result = loads(data)
    assert result == {
        "a": [1, 2, 3, 4],
        "b": 3,
    }


def test_mixed_overrides():
    data = """
    x: "x" // "x"
    y: ${x}"y" // "xy"
    x: ${y}"z" // "xyz"
    """
    result = loads(data)
    assert result == {
        "x": "xyz",
        "y": "xy"
    }


def test_empty_duplication():
    """When all elements of Unresolved Duplication resolve to UNDEFINED, the entire key should be removed."""
    data = """
        x: ${?y}
        x: ${?z}
        """
    result = loads(data)
    assert result == {}
