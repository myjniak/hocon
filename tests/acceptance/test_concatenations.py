from hocon import loads


def test_concatenation_of_test_with_subs():
    data = """
    x: 10
    y: 7
    z: [3,4]
    data: [1,2] ${z} [5,6,${?y},8] [9, ${x}] 
    """
    assert loads(data) == {
        "x": 10,
        "y": 7,
        "z": [3, 4],
        "data": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]
    }


def test_concatenation_of_lists_with_subs():
    data = """
    a: good
    b: bad
    c: If
    d: people
    data: To my mind"," there is no ${a} or ${b}"." ${c} I had to say what I value most in life", I'd" say ${d}
    """
    assert loads(data) == {
        "a": "good",
        "b": "bad",
        "c": "If",
        "d": "people",
        "data": "To my mind, there is no good or bad. If I had to say what I value most in life, I'd say people"
    }


def test_concatenation_of_non_strings_to_text():
    data = """
    x: 9.1
    y: 10
    data: About ${x}/${y} dentists recommends this library. 
    """
    assert loads(data) == {
        "x": 9.1,
        "y": 10,
        "data": "About 9.1/10 dentists recommends this library."
    }


def test_concatenation_of_dicts_with_subs():
    data = """
    x: {a:1}
    y: {e:5}
    z: {c:3}
    data: ${x} {b:2} ${y} {d:4} ${z}
    """
    assert loads(data) == {
        "x": {"a": 1},
        "y": {"e": 5},
        "z": {"c": 3},
        "data": {
            "a": 1,
            "b": 2,
            "c": 3,
            "d": 4,
            "e": 5
        }
    }
