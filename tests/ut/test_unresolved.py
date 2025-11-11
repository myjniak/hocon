import pytest

from hocon.exceptions import HOCONDuplicateKeyMergeError
from hocon.strings import UnquotedString
from hocon.unresolved import UnresolvedConcatenation, UnresolvedDuplication


def test_sanitize_empty_concatenation():
    concatenation = UnresolvedConcatenation([UnquotedString(" "), UnquotedString(" ")])
    sanitized = concatenation.sanitize()
    assert len(sanitized) == 0


def test_sanitize_empty_duplication():
    duplication = UnresolvedDuplication([])
    with pytest.raises(HOCONDuplicateKeyMergeError):
        duplication.sanitize()


def test_sanitize_duplication():
    duplication = UnresolvedDuplication([1, 2, {"a": 1}, 4, {"b": 2}, {"c": 3}])
    sanitized = duplication.sanitize()
    assert sanitized == UnresolvedDuplication([{"b": 2}, {"c": 3}])


def test_filter_unquoted_spaces():
    concatenation = UnresolvedConcatenation([{}, {}, UnquotedString("  "), {}, UnquotedString()])
    result = concatenation.filter_out_unquoted_space()
    assert result == [{}, {}, {}]


def test_filter_unquoted_spaces_2():
    concatenation = UnresolvedConcatenation([{}, UnquotedString(" Hi"), {}, UnquotedString()])
    result = concatenation.filter_out_unquoted_space()
    assert result == [{}, UnquotedString(" Hi"), {}]
