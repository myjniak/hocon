from hocon import loads


def test_substitution_dict_deduplication():
    data = """
    x = { d: 4 }
    data: { a: 1 }
    data: { b : 2 }
    data: { c: 3 } ${x} {e:5}
    data: {f:6}
    """
    assert loads(data) == {
        "x": {"d": 4},
        "data": {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6}
    }


def test_deduplication_cut_off():
    data = """
    x = { d: 4 }
    data: { a: 1 }
    data: [ b, 2 ]
    data: { c: 3 } ${x} {e:5}
    data: {f:6}
    """
    assert loads(data) == {
        "x": {"d": 4},
        "data": {"c": 3, "d": 4, "e": 5, "f": 6}
    }


def test_deduplication_cut_off_2():
    data = """
    x = { d: 4 }
    data: { a: 1 }
    data: { b: 2 }
    data: { c: 3 } ${x} {e:5}
    data: [6]
    """
    assert loads(data) == {
        "x": {"d": 4},
        "data": [6]
    }
