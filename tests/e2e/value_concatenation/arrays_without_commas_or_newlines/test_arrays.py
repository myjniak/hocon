import pytest

import hocon

pytestmark = pytest.mark.f10_4


def test_concatenated():
    data = """[ 1 2 3 4 ]"""
    result = hocon.loads(data)
    assert result == ["1 2 3 4"]


def test_newline_as_separator():
    data = """
    [ 1
      2
      3
      4 ]
    """
    result = hocon.loads(data)
    assert result == [1, 2, 3, 4]


def test_list_concatenation_inside_list():
    data = """[ [ 1, 2 ] [ 3, 4 ] ]"""
    result = hocon.loads(data)
    assert result == [[1, 2, 3, 4]]


def test_list_elements_separated_with_newline():
    data = """
    [ [ 1, 2 ]
      [ 3, 4 ] ]
    """
    result = hocon.loads(data)
    assert result == [[1, 2], [3, 4]]


def test_commas_with_unquoted():
    data = """
    name: John
    world: mom
    test: [ This is an unquoted string my name is ${name}, Hello ${world} ]
    """
    result = hocon.loads(data)
    assert result == {
        "name": "John",
        "world": "mom",
        "test": [
            "This is an unquoted string my name is John",
            "Hello mom"
        ]
    }


def test_commas_with_unquoted_2():
    data = """
    a = hi
    b = mom
    x = can I
    y = help you"?"
    test = [ ${a} ${b}, ${x} ${y} ]
    """
    result = hocon.loads(data)
    assert result == {
        "a": "hi",
        "b": "mom",
        "x": "can I",
        "y": "help you?",
        "test": [
            "hi mom",
            "can I help you?"
        ]
    }
