from hocon.strings import UnquotedString, QuotedString
from hocon.unresolved import UnresolvedConcatenation
from hocon.parser._parser import parse_dict_value


def test_1():
    value, _ = parse_dict_value("{c: 3} {d: 4},}", idx=0)
    assert value == UnresolvedConcatenation([
        {"c": UnresolvedConcatenation(["3"])},
        UnquotedString(" "),
        {"d": UnresolvedConcatenation(["4"])}
    ])


def test_2():
    value, _ = parse_dict_value("""  I "like"  pancakes , """, idx=0)
    assert value == UnresolvedConcatenation((
        UnquotedString("  "),
        UnquotedString("I"),
        UnquotedString(" "),
        QuotedString("like"),
        UnquotedString("  "),
        UnquotedString("pancakes"),
        UnquotedString(" ")
    ))
