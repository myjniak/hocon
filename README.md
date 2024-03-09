# HOCON parser with json-like interface

## Installation

```shell
pip install hocon
```

## Usage

Just like in python json module, you can load a string to python dictionary/list:

```python
import hocon

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
}
"""
dictionary = hocon.loads(data)
```

And you can dump it back to string:

```pycon
>>> print(hocon.dumps(dictionary, indent=4))
{
    "a": {
        "b": {
            "c": 7,
            "d": 8
        }
    }
}
```

## Specification

The library has NOT YET been tested according to each and every statement in
the [hocon specification](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md).
Check FEATURES.md to see which HOCON functionalities are already implemented and tested.
