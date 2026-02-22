import pytest

from hocon import loads
from hocon.parser import parse
from hocon.resolver._lazy_resolver import resolve


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


@pytest.mark.xfail
def test_multiple_appends():
    data = """
    a = [1,2]
    a += 3
    a += 4
    a += 5
    """
    assert loads(data) == {"a": [1, 2, 3, 4, 5]}


@pytest.mark.xfail
def test_nested_multiple_merges():
    data = """
    a.b = [1,2]
    a.b = ${a.b} [3,4]
    a.b = ${a.b} [5,6]
    """
    assert loads(data) == {"a": {"b": [1, 2, 3, 4, 5, 6]}}


@pytest.mark.xfail
def test_merge_list_with_undefined():
    data = """
    a.b = [1,2]
    a.b = ${?x}
    """
    assert loads(data) == {"a": {"b": [1, 2]}}


def test_merge_undefined():
    """According to https://github.com/lightbend/config implementation"""
    data = """
    a.b = ${?x}
    a.b = ${?y}
    """
    assert loads(data) == {"a": {}}


@pytest.mark.xfail
def test_merge_simple_with_undefined():
    """According to https://github.com/lightbend/config implementation"""
    data = """
    a.b = 1
    a.b = ${?x}
    """
    assert loads(data) == {"a": {"b": 1}}


@pytest.mark.xfail
def test_merge_simple_with_undefined_2():
    """According to https://github.com/lightbend/config implementation"""
    data = """
    a.b = 1
    a.b = ${?x}
    a.b = ${?y}
    """
    assert loads(data) == {"a": {"b": 1}}


def test_merge_undefined_with_dict():
    """b.a.b key resolves to undefined both in ${a} and in {b: ${?x}}. Make sure b.a.b is not created."""
    data = """
        a: {a: 1}
        b {
          a: ${a} {b: ${?x}}
        }
    """
    result = loads(data)
    assert result == {
        "a": {"a": 1},
        "b": {"a": {"a": 1}}
    }


def test_undefined_in_dict_overrides_it_all():
    """{c: ${?x}} resolves to {}, and dict overrides everything in key concatenation."""
    data = """
        a: {b: [1,2,3]} {b: {c: ${?x}}}
    """
    result = loads(data)
    assert result == {"a":{"b":{}}}


@pytest.mark.xfail
def test_merge_duplication_with_list():
    data = """
    a = {b: [2]}
    a = {b: ${?x}
         b: ${?y}
    }
    """
    result = loads(data)
    assert result == {"a": {"b": [2]}}


@pytest.mark.xfail
def test_merge_duplications():
    data = """
    a = {
      b: ${?x}
      b: ${?y}
    }
    a = {
      b: [2]
      b: ${?z}
    }
    """
    result = loads(data)
    assert result == {"a": {"b": [2]}}


def test_merging_while_ignoring_overriden_unresolvable():
    data = """
        a = ${x}
        a = 0
        a = {key: value}
        a = ${y}
        y = {key2: value2}
    """
    result = loads(data)
    assert result == {"a": {"key": "value", "key2": "value2"}, "y": {"key2": "value2"}}