import pytest

from hocon.parser._data import ParserInput
from hocon.strings import UnquotedString, QuotedString
from hocon.unresolved import UnresolvedConcatenation, UnresolvedDuplication, UnresolvedSubstitution
from hocon.parser._parser import parse_dict_value
from hocon._main import parse


def test_1():
    parser_input = ParserInput("{c: 3} {d: 4},}", "")
    value, _ = parse_dict_value(parser_input, idx=0, current_keypath=[])
    assert value == UnresolvedConcatenation([
        {"c": UnresolvedConcatenation(["3"])},
        UnquotedString(" "),
        {"d": UnresolvedConcatenation(["4"])}
    ])


def test_2():
    parser_input = ParserInput("""  I "like"  pancakes , """, "")
    value, _ = parse_dict_value(parser_input, idx=0, current_keypath=[])
    assert value == UnresolvedConcatenation((
        UnquotedString("  "),
        UnquotedString("I"),
        UnquotedString(" "),
        QuotedString("like"),
        UnquotedString("  "),
        UnquotedString("pancakes"),
        UnquotedString(" ")
    ))


def test_parse_all_unresolved_types():
    data = "a=[1,2], a=${?a}[3]"
    result = parse(data)
    expected = {
        "a": UnresolvedDuplication([
            UnresolvedConcatenation([
                [
                    UnresolvedConcatenation(["1"]),
                    UnresolvedConcatenation(["2"])
                ]
            ]),
            UnresolvedConcatenation([
                UnresolvedSubstitution(["a"], optional=True, relative_location=["a"]),
                [UnresolvedConcatenation(["3"])]
            ])
        ])
    }
    assert result == expected


@pytest.mark.f13_2
def test_parse_iadd():
    data = "a=[1,2], a=${?a}[3]"
    data_iadd = "a=[1,2], a+=3"
    assert parse(data) == parse(data_iadd)
