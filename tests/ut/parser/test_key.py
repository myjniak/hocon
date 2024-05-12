import pytest

from hocon.parser._data import ParserInput
from hocon.parser._key import parse_keypath


@pytest.mark.parametrize("data, expected", [
    ("1 \"key\"  : 0", ["1 key"]),
    ("key : 0", ["key"]),
    ("\"key  \"  : 0", ["key  "])
])
def test_parse_keypath(data: str, expected: list[str]):
    parser_input = ParserInput(data, "")
    keypath = parse_keypath(parser_input, 0)
    assert keypath.keys == expected
