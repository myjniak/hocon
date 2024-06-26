# HOCON parser with json-like interface

[![codecov](https://codecov.io/github/myjniak/hocon/graph/badge.svg?token=ZY5KK0BSJY)](https://codecov.io/github/myjniak/hocon)

## Installation

```shell
pip install hocon
```

## Usage

Just like in python json module, you can load a string to python dictionary/list:

```python
import hocon

data = """
animal.favorite: badger
key : ${animal.favorite} is my favorite animal
"""
dictionary = hocon.loads(data)
```

And you can dump it back to string:

```pycon
>>> print(hocon.dumps(dictionary, indent=4))
{
    "animal": {"favorite": "badger"},
    "key": "badger is my favorite animal"
}
```

## Specification

The library has NOT YET been tested according to each and every statement in
the [hocon specification](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md).
Check [FEATURES.md](https://github.com/myjniak/hocon/blob/main/FEATURES.md) to see which HOCON functionalities are already implemented and tested.
