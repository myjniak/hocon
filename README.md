# HOCON parser with json-like interface

[![codecov](https://codecov.io/github/myjniak/hocon/graph/badge.svg?token=ZY5KK0BSJY)](https://codecov.io/github/myjniak/hocon)

## Usage

Just like with json, you can load data from a file or from a string to python dict/list:

```python
import hocon

data = """
animal.favorite: badger
key : ${animal.favorite} is the best
"""
dictionary = hocon.loads(data)
```

And dump it back to string to your favorite format:

```pycon
>>> import yaml
>>> print(yaml.dump(dictionary))
animal:
  favorite: badger
key: badger is the best
```

## Specification

This library has NOT implemented each and every statement in
the [hocon specification](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md).

Check [FEATURES.md](https://github.com/myjniak/hocon/blob/main/FEATURES.md) to see which HOCON functionalities are already implemented and tested.

## Why choose hocon2?

- Simple interface
- Modern, fully py.typed design
- Tested on each change against:
    - black
    - mypy --strict
    - ruff
    - pylint
    - ALL conf examples from [hocon specification](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md)
    - 100% code coverage
    - typeguard (dynamic typechecks)
- Tested on demand against hypothesis generated confs
- Fixed a lot of issues still lingering in [pyhocon](https://github.com/chimpler/pyhocon/tree/master)

## Why choose pyhocon?

- You use python < 3.11
- You need a HOCON writer - hocon2 can only READ
- hocon2 is still in version 0.X.X, it might break backwards compatibility until version 1.0.0
- hocon2 has almost no users and no public issues raised so far (PROBABLY CONTAINS UNDISCOVERED BUGS)
- hocon2 is developed by a single person, responsiveness to issues and support might be worse than pyhocon
