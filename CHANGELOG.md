# Changelog
## 0.0.17
- Very basic implementation of include statement: {include "path/to/file.conf"} syntax supported only

## 0.0.16
- More tests for self-referential substitutions and cycle exceptions
- Fixed string concatenation with undefined substitutions

## 0.0.15
- Substitutions now store their location in the document
- Exception will be now raised when substitution points to its ancestor
- Self-referential substitution fallback fixed and covered with tests

## 0.0.14
- Support for optional ${?x} substitutions

## 0.0.13
- Support for substitution fallback to env vars

## 0.0.12
- Support for += operator

## 0.0.11
- Support for self-referential substitutions

## 0.0.10
- Added ${x} substitution parser 

## 0.0.9
- Split loads to parser and resolver

## 0.0.8
- Fixed multiline string corner cases

## 0.0.7
- Handled corner negative cases for unquoted strings

## 0.0.6
- More test coverage

## 0.0.5
- Added full support for commas
- Refactored source code a bit

## 0.0.3
- First draft, many features don't work yet
