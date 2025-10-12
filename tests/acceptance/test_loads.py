from hocon import loads
from hocon._main import parse


def test_1():
    result = loads("""{"dupa ":"heh"}""")
    assert result == {"dupa ": "heh"}


def test_2():
    result = loads("""{   dupsko =heh}""")
    assert result == {"dupsko": "heh"}


def test_3():
    result = loads("""{   dupsko {}}""")
    assert result == {"dupsko": {}}


def test_4():
    result = loads("""{   "2 dupska".heh {}}""")
    assert result == {"2 dupska": {"heh": {}}}


def test_5():
    result = loads("""{   "2 dupska" : 34.5e-2}""")
    assert result == {"2 dupska": 0.345}


def test_6():
    hocon = """t = {
                c = 5
                "d" = true
                e.y = {
                    f: 7
                    g: "hey dude!"
                    h: hey man
                    i = "first line"
                    
                }
                j = [1, 2, 3]
                u = 192.168.1.3/32
                g = null
            }
            """
    result = loads(hocon)
    assert result == {
        "t": {
            "c": 5,
            "d": True,
            "e": {
                "y": {
                    "f": 7,
                    "g": "hey dude!",
                    "h": "hey man",
                    "i": "first line"
                }
            },
            "j": [1, 2, 3],
            "u": "192.168.1.3/32",
            "g": None
        }
    }


def test_7():
    hocon = """{
                a: {
                    b: {
                        c = 5
                    }
                }
                a.b {
                    c = 7
                    d = 8
                }
            }
            """
    result = loads(hocon)
    assert result == {
        "a": {
            "b": {
                "c": 7,
                "d": 8
            }
        }
    }


def test_8():
    hocon = """
        a: {b: 1}
        a: {c: 2}
        b: {c: 3} {d: 4} {
            c: 5
        }
        """
    result = loads(hocon)
    assert result == {
        "a": {
            "b": 1,
            "c": 2,
        },
        "b": {
            "c": 5,
            "d": 4
        }
    }


def test_9():
    hocon = """
            a = a b c
            b = 5 b
            c = b 7
            """
    result = loads(hocon)
    assert result == {
        "a": "a b c",
        "b": "5 b",
        "c": "b 7"
    }


def test_10():
    hocon = """
            a = [1, 2] [3, 4] [
              5,
              6
            ]
            """
    result = loads(hocon)
    assert result == {
        "a": [1, 2, 3, 4, 5, 6]
    }


def test_11():
    data = """
        a: {a: 1}
        a: 5
        a: {b: 3} {b: 2}
        a: {c: 3}
        """
    result = loads(data)
    assert result == {
        "a": {"b": 2, "c": 3}
    }


def test_12():
    data = """
        a: {a: 1}
        a: {b: 2}
        a: {c: 3}
        """
    result = loads(data)
    assert result == {
        "a": {"a": 1, "b": 2, "c": 3}
    }


def test_13():
    data = """
        a: {a: 1}
        a: {b: 2}
        a: {c: 3}
        a: 10
        """
    result = loads(data)
    assert result == {"a": 10}


def test_14():
    data = """
            a = [1, 2] [3, 4] [
              5,
              6
            ]
            """
    result = loads(data)
    assert result == {
        "a": [1, 2, 3, 4, 5, 6]
    }


def test_15():
    data = """
            a = {a: 1} {b:2} {c:3}
            """
    result = loads(data)
    assert result == {
        "a": {"a": 1, "b": 2, "c": 3}
    }


def test_16():
    data = """
    a: {a: 1, b: 2}
    a: {a: 3, b: { c: ${a.a}, d: 4} {c: 6}}
    a: {a: 5, b: {c: 7}}
    """
    result = loads(data)
    assert result == {
        "a": {
            "a": 5,
            "b": {
                "c": 7
            }
        }

    }