"""String representation of parsed object should be readable"""

from hocon.unresolved import UnresolvedConcatenation


def test_concatenation():
    concatenation = UnresolvedConcatenation([1, 2, 3])
    assert str(concatenation) == '〈1, 2, 3〉'