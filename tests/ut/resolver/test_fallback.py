from hocon._main import parse, resolve
from hocon.resolver._resolver import cut_self_reference_and_fields_that_override_it


def test_cut_self_reference_and_fields_that_override_it():
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


def test_cut_self_reference_and_fields_that_override_it_2():
    data = """
    a: [1, 2]
    a: ${a}[3, 4]
    """
    parsed = parse(data)
    sub = parsed["a"][1][0]
    carved = cut_self_reference_and_fields_that_override_it(sub, parsed)
    result = resolve(carved)
    assert result == {"a": [1, 2]}
