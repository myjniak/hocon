## Features from spec

This table was made to make sure every section from specification gets ultimately covered and verified.
Tests written in pytest are tagged with feature ID.
For example tests for Array and object concatenation are marked with "f10_2" tag.

| Feature ID | Items                                                                                                                                                                  |    Implemented     |  Covered in tests  |
|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------:|:------------------:|
| f1         | [Unchanged from JSON](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#unchanged-from-json)                                                                    | :heavy_check_mark: | :heavy_check_mark: |
| f2         | [Comments](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#comments)                                                                                          | :heavy_check_mark: | :heavy_check_mark: |
| f3         | [Omit root braces](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#omit-root-braces)                                                                          | :heavy_check_mark: | :heavy_check_mark: |
| f4         | [Key-value separator](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#key-value-separator)                                                                    | :heavy_check_mark: | :heavy_check_mark: |
| f5         | [Commas](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#commas)                                                                                              | :heavy_check_mark: | :heavy_check_mark: |
| f6         | [Whitespace](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#whitespace)                                                                                      | :heavy_check_mark: |        :x:         |
| f7         | [Duplicate keys and object merging](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#duplicate-keys-and-object-merging)                                        | :heavy_check_mark: | :heavy_check_mark: |
| f8         | [Unquoted strings](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#unquoted-strings)                                                                          | :heavy_check_mark: | :heavy_check_mark: |
| f9         | [Multi-line strings](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#multi-line-strings)                                                                      | :heavy_check_mark: | :heavy_check_mark: |
| f10        | [Value concatenation](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#value-concatenation)                                                                    | :heavy_check_mark: | :heavy_check_mark: |
| f10_1      | [String value concatenation](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#string-value-concatenation)                                                      | :heavy_check_mark: | :heavy_check_mark: |
| f10_2      | [Array and object concatenation](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#array-and-object-concatenation)                                              | :heavy_check_mark: |  :yellow_circle:   |
| f10_3      | [Note: Concatenation with whitespace and substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#note-concatenation-with-whitespace-and-substitutions) |        :x:         |        :x:         |
| f10_4      | [Note: Arrays without commas or newlines](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#note-arrays-without-commas-or-newlines)                             | :heavy_check_mark: |        :x:         |
| f11        | [Path expressions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#path-expressions)                                                                          | :heavy_check_mark: |        :x:         |
| f12        | [Paths as keys](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#paths-as-keys)                                                                                | :heavy_check_mark: |        :x:         |
| f13        | [Substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#substitutions)                                                                                |        :x:         |        :x:         |
| f13_1      | [Self-referential substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#self-referential-substitutions)                                              |        :x:         |        :x:         |
| f13_2      | [The `+=` field separator](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#the--field-separator)                                                              |        :x:         |        :x:         |
| f13_3      | [Examples of Self-Referential Substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#examples-of-self-referential-substitutions)                      |        :x:         |        :x:         |
| f14        | [Includes](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#includes)                                                                                          |        :x:         |        :x:         |
| f14_1      | [Include syntax](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-syntax)                                                                              |        :x:         |        :x:         |
| f14_2      | [Include semantics: merging](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-merging)                                                       |        :x:         |        :x:         |
| f14_3      | [Include semantics: substitution](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-substitution)                                             |        :x:         |        :x:         |
| f14_4      | [Include semantics: missing files and required files](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-missing-files-and-required-files)     |        :x:         |        :x:         |
| f14_5      | [Include semantics: file formats and extensions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-file-formats-and-extensions)               |        :x:         |        :x:         |
| f14_6      | [Include semantics: locating resources](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-locating-resources)                                 |        :x:         |        :x:         |
| f15        | [Conversion of numerically-index objects to arrays](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#conversion-of-numerically-indexed-objects-to-arrays)      |        :x:         |        :x:         |


## Additional requirements

There are several assumptions which are not defined by the spec but are essential to the library health.

| Requirement ID | Requirement                                                             |
|----------------|-------------------------------------------------------------------------|
| r1             | If data is an invalid hocon, HOCONDecodeError exception will be raised. |
