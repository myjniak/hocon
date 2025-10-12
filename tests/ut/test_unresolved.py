import pytest

from hocon.exceptions import HOCONDuplicateKeyMergeError
from hocon.strings import UnquotedString
from hocon.unresolved import UnresolvedConcatenation, UnresolvedDuplicateValue


def test_sanitize_empty_concatenation():
    concatenation = UnresolvedConcatenation([UnquotedString(" "), UnquotedString(" ")])
    sanitized = concatenation.sanitize()
    assert len(sanitized) == 0


def test_sanitize_empty_duplication():
    concatenation = UnresolvedDuplicateValue([])
    with pytest.raises(HOCONDuplicateKeyMergeError):
        concatenation.sanitize()


def test_filter_unquoted_spaces():
    concatenation = UnresolvedConcatenation([{}, {}, UnquotedString("  "), {}, UnquotedString()])
    result = concatenation.filter_out_unquoted_space()
    assert result == [{}, {}, {}]


def test_filter_unquoted_spaces_2():
    concatenation = UnresolvedConcatenation([{}, UnquotedString(" Hi"), {}, UnquotedString()])
    result = concatenation.filter_out_unquoted_space()
    assert result == [{}, UnquotedString(" Hi"), {}]