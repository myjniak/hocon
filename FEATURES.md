## Features from spec

This table was made to make sure every section from specification gets ultimately covered and verified.
Tests written in pytest are tagged with feature ID.
For example tests for Array and object concatenation are marked with "f10_2" tag.

:heavy_check_mark: Done

:yellow_circle: Partially implemented

:x: Not done

:no_entry_sign: Not applicable for python / not planned for implementation

| Feature ID | Item                                                                                                                                                                   | Implemented        |                                     Notes                                     |
|------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-------------------|:-----------------------------------------------------------------------------:|
| f1         | [Unchanged from JSON](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#unchanged-from-json)                                                                    | :heavy_check_mark: |
| f2         | [Comments](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#comments)                                                                                          | :heavy_check_mark: |
| f3         | [Omit root braces](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#omit-root-braces)                                                                          | :heavy_check_mark: |
| f4         | [Key-value separator](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#key-value-separator)                                                                    | :heavy_check_mark: |
| f5         | [Commas](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#commas)                                                                                              | :heavy_check_mark: |
| f6         | [Whitespace](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#whitespace)                                                                                      | :heavy_check_mark: |
| f7         | [Duplicate keys and object merging](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#duplicate-keys-and-object-merging)                                        | :heavy_check_mark: |
| f8         | [Unquoted strings](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#unquoted-strings)                                                                          | :heavy_check_mark: |
| f9         | [Multi-line strings](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#multi-line-strings)                                                                      | :heavy_check_mark: |
| f10        | [Value concatenation](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#value-concatenation)                                                                    | :heavy_check_mark: |
| f10_1      | [String value concatenation](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#string-value-concatenation)                                                      | :heavy_check_mark: |
| f10_2      | [Array and object concatenation](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#array-and-object-concatenation)                                              | :heavy_check_mark: |
| f10_3      | [Note: Concatenation with whitespace and substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#note-concatenation-with-whitespace-and-substitutions) | :heavy_check_mark: |
| f10_4      | [Note: Arrays without commas or newlines](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#note-arrays-without-commas-or-newlines)                             | :heavy_check_mark: |
| f11        | [Path expressions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#path-expressions)                                                                          | :heavy_check_mark: |
| f12        | [Paths as keys](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#paths-as-keys)                                                                                | :heavy_check_mark: |
| f13        | [Substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#substitutions)                                                                                | :heavy_check_mark: |
| f13_1      | [Self-referential substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#self-referential-substitutions)                                              | :heavy_check_mark: |
| f13_2      | [The `+=` field separator](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#the--field-separator)                                                              | :heavy_check_mark: |
| f13_3      | [Examples of Self-Referential Substitutions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#examples-of-self-referential-substitutions)                      | :heavy_check_mark: |
| f14        | [Includes](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#includes)                                                                                          | :heavy_check_mark: |
| f14_1      | [Include syntax](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-syntax)                                                                              | :yellow_circle:    |              url() and classpath() keywords are not implemented.              |
| f14_2      | [Include semantics: merging](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-merging)                                                       | :heavy_check_mark: |
| f14_3      | [Include semantics: substitution](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-substitution)                                             | :heavy_check_mark: |
| f14_4      | [Include semantics: missing files and required files](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-missing-files-and-required-files)     | :yellow_circle:    |              url() and classpath() keywords are not implemented.              |
| f14_5      | [Include semantics: file formats and extensions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-file-formats-and-extensions)               | :x:                |
| f14_6      | [Include semantics: locating resources](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#include-semantics-locating-resources)                                 | :x:                |
| f15        | [Conversion of numerically-index objects to arrays](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#conversion-of-numerically-indexed-objects-to-arrays)      | :x:                |
| f16        | [Automatic type conversions](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#automatic-type-conversions)                                                      | :no_entry_sign:    |                 This library does not implement API features.                 |
| f17        | [Units format](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#units-format)                                                                                  | :no_entry_sign:    |        This library does not support "asking for data types". See f16.        |
| f18        | [Duration format](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#duration-format)                                                                            | :no_entry_sign:    |        This library does not support "asking for data types". See f16.        |
| f19        | [Period format](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#period-format)                                                                                | :no_entry_sign:    |        This library does not support "asking for data types". See f16.        |
| f20        | [Size in bytes format](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#size-in-bytes-format)                                                                  | :no_entry_sign:    |        This library does not support "asking for data types". See f16.        |
| f21        | [Config object merging and file merging](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#config-object-merging-and-file-merging)                              | :heavy_check_mark: |
| f22        | [Java properties mapping](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#java-properties-mapping)                                                            | :x:                |
| f23        | [Conventional configuration files for JVM apps](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#conventional-configuration-files-for-jvm-apps)                | :no_entry_sign:    | Feature intertwines too much with Java ecosystem to be implemented in python. |
| f24        | [Conventional override by system properties](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#conventional-override-by-system-properties)                      | :no_entry_sign:    | Feature intertwines too much with Java ecosystem to be implemented in python. |
| f25        | [Substitution fallback to environment variables](https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#substitution-fallback-to-environment-variables)              | :heavy_check_mark: |

## Additional requirements

There are several assumptions which are not defined by the HOCON spec but are essential to the library health and
convenient usage.

| Requirement ID | Requirement                                                       | Notes                                      |
|----------------|-------------------------------------------------------------------|--------------------------------------------|
| r1             | If data is an invalid hocon, HOCONError exception will be raised. | https://github.com/myjniak/hocon/issues/42 |

