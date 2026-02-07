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
        "data": {"a": 1, "b": 2, "c": 3, "d": 4, "e": 5, "f": 6},
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
        "data": {"c": 3, "d": 4, "e": 5, "f": 6},
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
        "data": [6],
    }


def test_nested_dicts_simple_value_cutoff():
    """As with duplicate keys, an intermediate non-object value "hides" earlier object values.
    42 simply wins and loses all information about what it overrode.
    """
    data = """
    p: {"a" : { "y" : 2 }}
    p: {"a" : 42}
    p: {"a" : { "x" : 1 }}
    """
    assert loads(data) == {"p": {"a": {"x": 1}}}


def test_nested_dicts():
    data = """
    p: {"a" : 42}
    p: {"a" : { "y" : 2 }}
    p: {"a" : { "x" : 1 }}
    """
    assert loads(data) == {"p": {"a": {"x": 1, "y": 2}}}
