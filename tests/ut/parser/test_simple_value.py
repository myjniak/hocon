import pytest

from hocon.exceptions import HOCONUnexpectedSeparatorError
from hocon.parser._simple_value import parse_simple_value
from hocon.strings import UnquotedString, QuotedString
from hocon.unresolved import UnresolvedSubstitution, UnresolvedDuplicateValue, UnresolvedConcatenation


def test_parse_simple_value():
    data = """  I  "like"  pancakes ,"""
    result = parse_simple_value(data, 0)
    assert result == (UnquotedString("  "), 2)
    result = parse_simple_value(data, 2)
    assert result == (UnquotedString("I"), 3)
    result = parse_simple_value(data, 3)
    assert result == (UnquotedString("  "), 5)
    result = parse_simple_value(data, 5)
    assert result == (QuotedString("like"), 11)
    result = parse_simple_value(data, 11)
    assert result == (UnquotedString("  "), 13)
    result = parse_simple_value(data, 13)
    assert result == (UnquotedString("pancakes"), 21)
    result = parse_simple_value(data, 21)
    assert result == (UnquotedString(" "), 22)
    with pytest.raises(HOCONUnexpectedSeparatorError):
        parse_simple_value(data, 22)


@pytest.mark.f13
@pytest.mark.parametrize("data, expected", [
    ("${path.expression}", UnresolvedSubstitution(["path", "expression"], optional=False)),
    ("${?path.expression}", UnresolvedSubstitution(["path", "expression"], optional=True))
])
def test_parse_substitution(data: str, expected: UnresolvedSubstitution):
    result, _ = parse_simple_value(data)
    assert result == expected
