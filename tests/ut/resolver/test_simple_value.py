from hocon.resolver._simple_value import resolve_simple_value
from hocon.strings import QuotedString, UnquotedString


def test_1():
    data = [UnquotedString("  "), UnquotedString("43.2"), UnquotedString(" ")]
    result = resolve_simple_value(data)
    assert result == 43.2


def test_2():
    data = [QuotedString("  "), UnquotedString("43.2"), UnquotedString(" ")]
    result = resolve_simple_value(data)
    assert result == "  43.2"


def test_3():
    data = [UnquotedString("  "), QuotedString("43.2"), UnquotedString(" ")]
    result = resolve_simple_value(data)
    assert result == "43.2"
