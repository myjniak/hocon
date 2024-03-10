"""duplicate keys that appear later override those that appear earlier, unless both values are objects."""
import hocon
import pytest

pytestmark = pytest.mark.f7


def test_str():
    data = """a.b="hi"
    a {
      a: hi
      b: hi mom
    }
    a.a : hi dad
    """
    result = hocon.loads(data)
    assert result == {
        "a": {
            "a": "hi dad",
            "b": "hi mom"
        }
    }


def test_int():
    data = """a.b=0
        a {
          a: 0
          b: 2
        }
        a.a : 1
        """
    result = hocon.loads(data)
    assert result == {
        "a": {
            "a": 1,
            "b": 2
        }
    }

def test_other_simple():
    data = """a.b=null
        a {
          a: -Infinity
          b: false
        }
        a.a : true
        """
    result = hocon.loads(data)
    assert result == {
        "a": {
            "a": True,
            "b": False
        }
    }


def test_list():
    data = """a.b=[1,2,]
        a {
          a: [69]
          b: [hi dad]
        }
        a.a : [hi, mom]
        """
    result = hocon.loads(data)
    assert result == {
        "a": {
            "a": ["hi", "mom"],
            "b": ["hi dad"]
        }
    }
