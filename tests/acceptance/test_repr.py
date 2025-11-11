"""String representation of parsed object should be readable"""
import json

from hocon.unresolved import UnresolvedConcatenation


def test_concatenation():
    concatenation = UnresolvedConcatenation([1, 2, 3])
    print(json.dumps(concatenation))
    assert str(concatenation) == """〈
  "1",
  "2",
  "3"
〉"""
