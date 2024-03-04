import json
from src._parser import merge


def test_1():
    dictionary = {
        "a": {
            "b": 0,
            "c": 1,
            "d": {
                "e": 2,
                "f": {
                    "g": 3,
                    "h": 4
                }
            }
        },
        "b": {}
    }
    key = "a"
    value = {
        "a": 3,
        "c": 4,
        "d": {
            "f": {
                "h": 5,
                "i": 6
            }
        }
    }
    output = merge(dictionary, {key: value})
    print(json.dumps(output, indent=4))
    assert output == {
        "a": {
            "b": 0,
            "c": 4,
            "d": {
                "e": 2,
                "f": {
                    "g": 3,
                    "h": 5,
                    "i": 6
                }
            },
            "a": 3
        },
        "b": {}
    }


def test_2():
    dictionary = {
        "a": 0,
        "b": 1
    }
    key = "a"
    value = 2
    output = merge(dictionary, {key: value})
    print(json.dumps(output, indent=4))
    assert output == {
        "a": 2,
        "b": 1
    }


def test_3():
    dictionary = {
        "a": 0,
        "b": 1
    }
    key = "a"
    value = {}
    output = merge(dictionary, {key: value})
    print(json.dumps(output, indent=4))
    assert output == {
        "a": {},
        "b": 1
    }
