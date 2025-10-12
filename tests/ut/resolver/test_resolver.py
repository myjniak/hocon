from hocon.strings import UnquotedString
from hocon.unresolved import UnresolvedConcatenation


def test_1():
    concatenation = UnresolvedConcatenation([{}, {}, UnquotedString("  "), {}, UnquotedString()])
    result = concatenation.filter_out_unquoted_space()
    assert result == [{}, {}, {}]


def test_2():
    concatenation = UnresolvedConcatenation([{}, UnquotedString(" Hi"), {}, UnquotedString()])
    result = concatenation.filter_out_unquoted_space()
    assert result == [{}, UnquotedString(" Hi"), {}]
