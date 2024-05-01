"""
To merge objects:

- add fields present in only one of the two objects to the merged object.
- for non-object-valued fields present in both objects,
 the field found in the second object must be used.
- for object-valued fields present in both objects,
 the object values should be recursively merged according to these same rules.
"""
import hocon
import pytest

pytestmark = pytest.mark.f7


def test_merge():
    data = """
    {
    "foo" : { "a" : 42 },
    "foo" : { "b" : 43 }
    }
    """
    result = hocon.loads(data)
    assert result == {
        "foo": {"a": 42, "b": 43}
    }


def test_override_dict():
    """
    Object merge can be prevented by setting the key to another value first.
    This is because merging is always done two values at a time;
    if you set a key to an object, a non-object, then an object,
    first the non-object falls back to the object (non-object always wins),
    and then the object falls back to the non-object (no merging, object is the new value).
    So the two objects never see each other.
    """
    data = """{
    "foo" : { "a" : 42 },
    "foo" : null,
    "foo" : { "b" : 43 }
    }"""
    result = hocon.loads(data)
    assert result == {
        "foo": {"b": 43}
    }


def test_recursive_merge():
    data = """{
                a: {
                    b: {
                        c = 5
                    }
                }
                a.b {
                    c = 7
                    d = 8
                }
                a.b.e = 9
            }
            """
    result = hocon.loads(data)
    print(result)
    # assert result == {
    #     "a": {
    #         "b": {
    #             "c": 7,
    #             "d": 8,
    #             "e": 9
    #         }
    #     }
    # }
