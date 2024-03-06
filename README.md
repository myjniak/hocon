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
the [hocon specification](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md)

## Syntax features covered by tests

| Feature ID | Items                                                                                                                                                                  |    Covered in tests     |
|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------------:|
| 1          | [Unchanged from JSON](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#unchanged-from-json)                                                                    |   :white_check_mark:    |
| 2          | [Comments](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#comments)                                                                                          |           :x:           |
| 3          | [Omit root braces](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#omit-root-braces)                                                                          |           :x:           |
| 4          | [Key-value separator](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#key-value-separator)                                                                    |           :x:           |
| 5          | [Commas](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#commas)                                                                                              |           :x:           |
| 6          | [Whitespace](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#whitespace)                                                                                      |   :white_check_mark:    |
| 7          | [Duplicate keys and object merging](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#duplicate-keys-and-object-merging)                                        |           :x:           |
| 8          | [Unquoted strings](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#duplicate-keys-and-object-merging)                                                         |           :x:           |
| 9          | [Multi-line strings](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#multi-line-strings)                                                                      |           :x:           |
| 10         | [Value concatenation](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#value-concatenation)                                                                    |           :x:           |
| 10.1       | [String value concatenation](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#string-value-concatenation)                                                      |           :x:           |
| 10.2       | [Array and object concatenation](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#array-and-object-concatenation)                                              |           :x:           |
| 10.3       | [Note: Concatenation with whitespace and substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#note-concatenation-with-whitespace-and-substitutions) |           :x:           |
| 10.4       | [Note: Arrays without commas or newlines](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#note-arrays-without-commas-or-newlines)                             |           :x:           |
| 11         | [Path expressions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#path-expressions)                                                                          |           :x:           |
| 12         | [Paths as keys](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#paths-as-keys)                                                                                |           :x:           |
| 13         | [Substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#substitutions)                                                                                |           :x:           |
| 13.1       | [Self-referential substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#self-referential-substitutions)                                              |           :x:           |
| 13.2       | [The `+=` field separator](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#the--field-separator)                                                              |           :x:           |
| 13.3       | [Examples of Self-Referential Substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#examples-of-self-referential-substitutions)                      |           :x:           |
| 14         | [Includes](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#includes)                                                                                          |           :x:           |
| 14.1       | [Include syntax](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-syntax)                                                                              |           :x:           |
| 14.2       | [Include semantics: merging](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-merging)                                                       |           :x:           |
| 14.3       | [Include semantics: substitution](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-substitution)                                             |           :x:           |
| 14.4       | [Include semantics: missing files and required files](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-missing-files-and-required-files)     |           :x:           |
| 14.5       | [Include semantics: file formats and extensions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-file-formats-and-extensions)               |           :x:           |
| 14.6       | [Include semantics: locating resources](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-locating-resources)                                 |           :x:           |
| 15         | [Conversion of numerically-index objects to arrays](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#conversion-of-numerically-indexed-objects-to-arrays)      |           :x:           |