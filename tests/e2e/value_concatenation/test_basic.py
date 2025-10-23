"""The value of an object field or array element may consist of multiple values which are combined.
There are three kinds of value concatenation:
"""
import pytest

import hocon

pytestmark = pytest.mark.f10


def test_simple_value():
    """If all the values are simple values (neither objects nor arrays), they are concatenated into a string_."""
    data = 'a= 12 """carrots""" in "my pocket"'
    result = hocon.loads(data)
    assert result == {
        "a": "12 carrots in my pocket",
    }


def test_arrays():
    """If all the values are arrays, they are concatenated into one array."""
    data = "a= [12, carrots] [in, my] [ pocket,]"
    result = hocon.loads(data)
    assert result == {
        "a": [12, "carrots", "in", "my", "pocket"],
    }


def test_dictionaries():
    """If all the values are objects, they are merged (as with duplicate keys) into one object."""
    data = 'a= {in: your} {12: carrots} {in= my} { pocket: "."}'
    result = hocon.loads(data)
    assert result == {
        "a": {"12": "carrots", "in": "my", "pocket": "."},
    }


def test_allowed_places_to_concatenate():
    """String value concatenation is allowed in field keys, in addition to field values and array elements."""
    data = ('1 concatenated "key"  :   it   is 12 "o`clock",'
            'list: ["oh"  "I" will find """you""" and I will, concatenate you ]')
    result = hocon.loads(data)
    assert result == {
        "1 concatenated key": "it   is 12 o`clock",
        "list": ["oh  I will find you and I will", "concatenate you"],
    }
