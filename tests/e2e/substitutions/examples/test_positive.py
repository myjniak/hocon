import hocon


def test_regular_fallback():
    data = """
    foo : { a : 1 }
    foo : ${foo}
    """
    result = hocon.loads(data)
    assert result == {
        "foo": {"a": 1}
    }


def test_disappearing_field():
    data = """foo : ${?foo} // this field just disappears silently"""
    result = hocon.loads(data)
    assert result == {}


def test_hidden_sub():
    data = """
    foo : ${does-not-exist}
    foo : 42"""
    result = hocon.loads(data)
    assert result == {"foo": 42}


def test_hidden_sub_2():
    data = """
    foo : ${foo}
    foo : 42"""
    result = hocon.loads(data)
    assert result == {"foo": 42}


def test_resolve_to_value_below():
    """Here, ${foo.a} would refer to { c : 1 } rather than 2"""
    data = """
    foo : { a : { c : 1 } }
    foo : ${foo.a}
    foo : { a : 2 }"""
    result = hocon.loads(data)
    assert result == {"foo": {"a": 2, "c": 1}}


def test_allow_to_refer_to_paths_within_themselves():
    data = """
    bar : { foo : 42,
    baz : ${bar.foo}
    }"""
    result = hocon.loads(data)
    assert result == {
        "bar": {
            "foo": 42,
            "baz": 42
        }
    }


def test_no_cycle_when_looking_at_path_within_itself():
    data = """
    bar : { foo : 42,
            baz : ${bar.foo}
          }
    bar : { foo : 43 }"""
    result = hocon.loads(data)
    assert result == {
        "bar": {
            "foo": 43,
            "baz": 43
        }
    }


def test_mutually_referring_objects():
    data = """
    // bar.a should end up as 4
    bar : { a : ${foo.d}, b : 1 }
    bar.b = 3
    // foo.c should end up as 3
    foo : { c : ${bar.b}, d : 2 }
    foo.d = 4"""
    result = hocon.loads(data)
    assert result == {
        "bar": {
            "a": 4,
            "b": 3
        },
        "foo": {
            "c": 3,
            "d": 4
        }
    }


def test_optional_self_ref_in_value_concatenation():
    data = """a = ${?a}foo"""
    result = hocon.loads(data)
    assert result == {"a": "foo"}
