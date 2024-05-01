from hocon.resolver._utils import filter_out_unquoted_space
from hocon.strings import UnquotedString


def test_1():
    result = filter_out_unquoted_space([{}, {}, UnquotedString("  "), {}, UnquotedString()])
    assert result == [{}, {}, {}]


def test_2():
    result = filter_out_unquoted_space([{}, UnquotedString(" Hi"), {}, UnquotedString()])
    assert result == [{}, UnquotedString(" Hi"), {}]
