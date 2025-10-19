# Changelog

## 0.2.0
- Various bugfixes in resolving self-referential substitutions
- Changes in Exception raises in certain scenarios
- Big change in resolve algorithm approach:
  1. parse
  2. resolve what can be resolved without touching substitutions
  3. resolve all substitutions
- Step 2 has been added to get rid of self.lazy attribute and self.lazy ifology in Resolver.

## 0.1.0
- Substitutions are looking at app root config as 1st priority AND (NEW) at relative included file keypath as 2nd priority.

## 0.0.19
- Separated substitution resolving to a separate module
- Fixed a bug where substitution was incorrectly detecting a cycle (bad detecting of pointing to self parent)
- Fixed a bug where comments can stuck key reading till the end of the config

## 0.0.18
- include statement and filepath can now be separated by newline
- Proper exception is raised if included file is an array

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
