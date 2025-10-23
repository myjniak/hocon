"""If a key is a path expression with multiple elements,
it is expanded to create an object for each path element other than the last.
The last path element, combined with the value, becomes a field in the most-nested object.
"""
from pathlib import Path

import pytest

import hocon
from tests.utils import set_env

pytestmark = pytest.mark.f13


def test_not_parsed_inside_quoted_string():
    data = """
    animal.favorite: badger
    key : "${animal.favorite} is my favorite animal"
    """
    result = hocon.loads(data)
    assert result == {
        "animal": {"favorite": "badger"},
        "key": "${animal.favorite} is my favorite animal",
    }


def test_substituion_in_unquoted_concatenation():
    """To get a string containing a substitution,
    you must use value concatenation with the substitution in the unquoted portion
    """
    data = """
    animal.favorite: badger
    key : ${animal.favorite} is my favorite animal
    """
    result = hocon.loads(data)
    assert result == {
        "animal": {"favorite": "badger"},
        "key": "badger is my favorite animal",
    }


def test_substituion_in_concatenation():
    """You could also quote the non-substitution portion"""
    data = """
    animal.favorite: badger
    key : ${animal.favorite}" is my favorite animal"
    """
    result = hocon.loads(data)
    assert result == {
        "animal": {"favorite": "badger"},
        "key": "badger is my favorite animal",
    }


def test_substitution_path_is_absolute():
    """Substitutions are resolved by looking up the path in the configuration.
    The path begins with the root configuration object, i.e. it is "absolute" rather than "relative".

    Substitution processing is performed as the last parsing step,
    so a substitution can look forward in the configuration.
    """
    data = """
    a: {
        b: {
            c: nested
            d: ${c}
            e: ${a.b.c}
        }
    }
    c: absolute
    """
    result = hocon.loads(data)
    assert result == {
        "a": {
            "b": {
                "c": "nested",
                "d": "absolute",
                "e": "nested",
            },
        },
        "c": "absolute",
    }


def test_substitution_from_env_var():
    """For substitutions which are not found in the configuration tree,
    implementations may try to resolve them by looking at system environment variables
    or other external sources of configuration.
    """
    data = """
    key: ${MY_HOCON_ENV_VAR}
    """
    with set_env(MY_HOCON_ENV_VAR="HELLO"):
        result = hocon.loads(data)
    assert result == {
        "key": "HELLO",
    }


def test_retrieve_value_from_another_file():
    conf_filepath = Path(__file__).parent / "data" / "main.conf"
    result = hocon.load(open(conf_filepath))
    assert result == {
        "key": "badger is my favorite animal",
        "animal": {
            "favorite": "badger",
        },
    }


def test_evaluate_to_latest_value():
    """If a key has been specified more than once, the substitution will always evaluate to its latest-assigned value
    (that is, it will evaluate to the merged object, or the last non-object value that was set,
    in the entire document being parsed including all included files).
    """
    data = """
    a: {a: 1}
    b: ${a}
    a: {b: 2}
    a: {c: 3}
    """
    result = hocon.loads(data)
    assert result == {
        "a": {"a": 1, "b": 2, "c": 3},
        "b": {"a": 1, "b": 2, "c": 3},
    }


def test_value_null_also_prevents_from_looking_to_env():
    """If a configuration sets a value to null then it should not be looked up in the external source."""
    data = """
    "HOME": null,
    a: ${HOME}
    """
    with set_env(HOME="/path/to/home"):
        result = hocon.loads(data)
    assert result == {
        "HOME": None,
        "a": None,
    }


def test_substitution_can_be_anything():
    """A substitution is replaced with any value type (number, object, string, array, true, false, null)."""
    data = """
    a = 3.14
    b = {a: a}
    c = string
    d = [1, 2, 3]
    e = true
    f = false
    g = null
    subs: [${a}, ${b}, ${c}, ${d}, ${e}, ${f}, ${g}]
    """
    result = hocon.loads(data)
    assert result == {
        "a": 3.14,
        "b": {"a": "a"},
        "c": "string",
        "d": [1, 2, 3],
        "e": True,
        "f": False,
        "g": None,
        "subs": [3.14, {"a": "a"}, "string", [1, 2, 3], True, False, None],
    }
