"""If a substitution with the ${?foo} syntax is undefined"""
import pytest

import hocon

pytestmark = pytest.mark.f13


def test_substitution_as_value_of_dict_key():
    """if it is the value of an object field then the field should not be created."""
    data = """
    movie.favorite: Rrrrrrrrr
    favorites : {
        animal: ${?animal.favorite}
        movie: ${?movie.favorite}
    }
    """
    result = hocon.loads(data)
    assert result == {
        "movie": {"favorite": "Rrrrrrrrr"},
        "favorites": {
            "movie": "Rrrrrrrrr"
        }
    }


def test_substitution_as_override_value_of_dict_key():
    """If the field would have overridden a previously-set value for the same field, then the previous value remains."""
    data = """
    movie.favorite: Rrrrrrrrr
    favorites : {
        animal: cat
        animal: ${?animal.favorite}
        movie: ${?movie.favorite}
    }
    """
    result = hocon.loads(data)
    assert result == {
        "movie": {"favorite": "Rrrrrrrrr"},
        "favorites": {
            "animal": "cat",
            "movie": "Rrrrrrrrr"
        }
    }


def test_substitution_as_list_element():
    """if it is an array element then the element should not be added."""
    data = "[a, b, ${?c}, d]"
    result = hocon.loads(data)
    assert result == ["a", "b", "d"]


def test_substitution_as_part_of_string_concatenation():
    """if it is part of a value concatenation with another string then it should become an empty string"""
    data = """[Tommy has ${?n} balloons]"""
    result = hocon.loads(data)
    assert result == ["Tommy has  balloons"]


def test_substitution_as_part_of_dict_concatenation():
    """if part of a value concatenation with an object or array it should become an empty object or array."""
    data = """
    a = {a: 1}
    sum = ${a} {b: 2} ${?c} {d: 4} 
    """
    result = hocon.loads(data)
    assert result == {
        "a": {"a": 1},
        "sum": {"a": 1, "b": 2, "d": 4}
    }


def test_substitution_as_part_of_list_concatenation():
    """if part of a value concatenation with an object or array it should become an empty object or array."""
    data = """
    a = 1
    sum = [${a}, 2, ${?c}, 4]
    """
    result = hocon.loads(data)
    assert result == {
        "a": 1,
        "sum": [1, 2, 4]
    }


def test_avoid_creating_fields():
    data = """foo : ${?bar}"""
    result = hocon.loads(data)
    assert result == {}


def test_avoid_creating_fields_2():
    data = """foo : ${?bar}${?baz}"""
    result = hocon.loads(data)
    assert result == {}


def test_deduplicate_undefined():
    data = """
    a = {a=1}
    a = ${?x}
    a = {b=2}
    a = ${?x}
    a = ${?x}
    """
    result = hocon.loads(data)
    assert result == {
        "a": {
            "a": 1,
            "b": 2
        }
    }
