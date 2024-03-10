## Features from spec

This table was made to make sure every section from specification gets ultimately covered and verified.
Tests written in pytest are tagged with feature ID.
For example tests for Array and object concatenation are marked with "f10.2" tag.

| Feature ID | Items                                                                                                                                                                  |  Covered in tests  |
|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------:|
| f1         | [Unchanged from JSON](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#unchanged-from-json)                                                                    | :white_check_mark: |
| f2         | [Comments](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#comments)                                                                                          | :white_check_mark: |
| f3         | [Omit root braces](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#omit-root-braces)                                                                          | :white_check_mark: |
| f4         | [Key-value separator](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#key-value-separator)                                                                    | :white_check_mark: |
| f5         | [Commas](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#commas)                                                                                              | :white_check_mark: |
| f6         | [Whitespace](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#whitespace)                                                                                      |        :x:         |
| f7         | [Duplicate keys and object merging](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#duplicate-keys-and-object-merging)                                        | :white_check_mark: |
| f8         | [Unquoted strings](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#unquoted-strings)                                                                          | :white_check_mark: |
| f9         | [Multi-line strings](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#multi-line-strings)                                                                      |        :x:         |
| f10        | [Value concatenation](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#value-concatenation)                                                                    |        :x:         |
| f10.1      | [String value concatenation](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#string-value-concatenation)                                                      |        :x:         |
| f10.2      | [Array and object concatenation](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#array-and-object-concatenation)                                              |        :x:         |
| f10.3      | [Note: Concatenation with whitespace and substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#note-concatenation-with-whitespace-and-substitutions) |        :x:         |
| f10.4      | [Note: Arrays without commas or newlines](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#note-arrays-without-commas-or-newlines)                             |        :x:         |
| f11        | [Path expressions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#path-expressions)                                                                          |        :x:         |
| f12        | [Paths as keys](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#paths-as-keys)                                                                                |        :x:         |
| f13        | [Substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#substitutions)                                                                                |        :x:         |
| f13.1      | [Self-referential substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#self-referential-substitutions)                                              |        :x:         |
| f13.2      | [The `+=` field separator](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#the--field-separator)                                                              |        :x:         |
| f13.3      | [Examples of Self-Referential Substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#examples-of-self-referential-substitutions)                      |        :x:         |
| f14        | [Includes](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#includes)                                                                                          |        :x:         |
| f14.1      | [Include syntax](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-syntax)                                                                              |        :x:         |
| f14.2      | [Include semantics: merging](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-merging)                                                       |        :x:         |
| f14.3      | [Include semantics: substitution](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-substitution)                                             |        :x:         |
| f14.4      | [Include semantics: missing files and required files](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-missing-files-and-required-files)     |        :x:         |
| f14.5      | [Include semantics: file formats and extensions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-file-formats-and-extensions)               |        :x:         |
| f14.6      | [Include semantics: locating resources](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-locating-resources)                                 |        :x:         |
| f15        | [Conversion of numerically-index objects to arrays](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#conversion-of-numerically-indexed-objects-to-arrays)      |        :x:         |


## Additional requirements

There are several assumptions which are not defined by the spec but are essential to the library health.

| Requirement ID | Requirement                                                             | Covered in tests |
|----------------|-------------------------------------------------------------------------|:----------------:|
| r1             | If data is an invalid hocon, HOCONDecodeError exception will be raised. |       :x:        |
