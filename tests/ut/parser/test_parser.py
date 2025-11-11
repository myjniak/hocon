import pytest

from hocon import loads
from hocon.parser import parse
from hocon.parser._data import ParserInput
from hocon.parser._parser import parse_dict_value
from hocon.resolver import _lazy_resolver, resolve
from hocon.strings import QuotedString, UnquotedString
from hocon.unresolved import (
    UnresolvedConcatenation,
    UnresolvedDuplication,
    UnresolvedSubstitution,
)


def test_two_dicts_concatenation():
    parser_input = ParserInput("{c: 3} {d: 4},}", "")
    value, _ = parse_dict_value(parser_input, idx=0, current_keypath=[])
    assert value == UnresolvedConcatenation([
        {"c": UnresolvedConcatenation(["3"])},
        UnquotedString(" "),
        {"d": UnresolvedConcatenation(["4"])},
    ])


def test_string_mix():
    parser_input = ParserInput("""  I "like"  pancakes , """, "")
    value, _ = parse_dict_value(parser_input, idx=0, current_keypath=[])
    assert value == UnresolvedConcatenation((
        UnquotedString("  "),
        UnquotedString("I"),
        UnquotedString(" "),
        QuotedString("like"),
        UnquotedString("  "),
        UnquotedString("pancakes"),
        UnquotedString(" "),
    ))


def test_parse_all_unresolved_types():
    data = "a=[1,2], a=${?a}[3]"
    result = parse(data)
    expected = {
        "a": UnresolvedDuplication([
            UnresolvedConcatenation([
                [
                    UnresolvedConcatenation(["1"]),
                    UnresolvedConcatenation(["2"]),
                ],
            ]),
            UnresolvedConcatenation([
                UnresolvedSubstitution(["a"], optional=True, relative_location=["a"]),
                [UnresolvedConcatenation(["3"])],
            ]),
        ]),
    }
    assert result == expected


@pytest.mark.f13_2
def test_parse_iadd():
    data = "a=[1,2], a=${?a}[3]"
    data_iadd = "a=[1,2], a+=3"
    assert parse(data) == parse(data_iadd)


def test_unresolved_include():
    data = """{
     a: 1
     include "i_dont_exist.conf"
     c: 3
     }"""

    resolved = loads(data)
    assert resolved == {"a": 1, "c": 3}
