from hocon._main import parse, resolve
from hocon import loads


def test_1():
    data = """
    d = {e: 1, f.g: [3, {4: 4, 99: ${x}}, 6]}      ,
    d = {e: 2}
    a = ${d.f.g.1.99}
    x = ${d.e}
    """
    result = loads(data)
    assert result == {
        'd': {
            'e': 2,
            'f': {
                'g': [
                    3, {'4': 4, '99': 2}, 6]
            }
        },
        'a': 2,
        'x': 2}


def test_2():
    data = """
    a: ${b} 
    b: 3 
    """
    result = loads(data)
    assert result == {
        "a": 3,
        "b": 3
    }


def test_3():
    data = """
            a = {a: 1} {b:${a.a}} {c:3}
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
    result = loads(data)
    expected = {
        "a": {
            "a": 4,
            "b": 5,
            "c": 6
        }
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
            "c": 3
        }
    }
    assert result == expected


def test_6():
    data = """
            a : [ 1, 2 ]
            a : ${a} [ 3, 4 ]
            """
    result = loads(data)
    print(result)
    # assert result == {
    #     "a": [1, 2, 3, 4]
    # }
