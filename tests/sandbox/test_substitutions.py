from hocon._main import parse, resolve
from hocon import loads


def test_1():
    data = """
    d = {e: amen "jea", f.g: [hihi, {253: 78, 156: ${x}}, 2]}      ,
    d = {e: egzakra}
    a = ${d.f.g.1.156}
    x = ${d.e}
    """
    x = parse(data)
    y = resolve(x)
    print(y)


def test_2():
    data = """
    a: ${b} 
    b: 3 
    """
    result = loads(data)
    print(result)


def test_3():
    data = """
            a = {a: 1} {b:${?a.a}} {c:3}
            """
    parsed = parse(data)
    resolved = resolve(parsed)
    assert resolved == {
        "a": {"a": 1, "b": 1, "c": 3}
    }


def test_4():
    data = """
            a = {a: 1} {b:hi ${a.a} mom} {c:3}
            a: {a: 4} {b: 5} {c: 6}
            """
    parsed = parse(data)
    resolved = resolve(parsed)
    expected = {
        "a": {
            "a": 4,
            "b": 5,
            "c": 6
        }
    }
    assert resolved == expected
