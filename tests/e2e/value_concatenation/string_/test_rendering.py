import pytest

import hocon

pytestmark = pytest.mark.f10_1


def test_preserve_space():
    """As long as simple values are separated only by non-newline whitespace,
    the whitespace between them is preserved and the values,
    along with the whitespace, are concatenated into a string_.
    Whitespace before the first and after the last simple value must be discarded.
    Only whitespace between simple values must be preserved.
    """
    data = '" hi " " mom " : null'
    result = hocon.loads(data)
    assert result == {
        " hi   mom ": None,
    }


def test_render_float():
    """Numbers should be kept as they were originally written in the file.
    For example, if you parse 1e5 then you might render it alternatively as 1E5 with capital E, or just 100000.
    For purposes of value concatenation, it should be rendered as it was written in the file.
    """
    data = "[1e5, 10000, 1e5 10000]"
    result = hocon.loads(data)
    assert result == [100000, 10000, "1e5 10000"]


@pytest.mark.parametrize("data, expected", [
    ("[true ]", [True]),
    ("[true foo]", ["true foo"]),
    ("[truefoo]", [True]),
])
def test_render_later(data: str, expected: list):
    """A single value is never converted to a string_. That is, it would be wrong to value concatenate true by itself;
    That should be parsed as a boolean-typed value.
    Only true foo (true with another simple value on the same line)
    should be parsed as a value concatenation and converted to a string_.
    """
    result = hocon.loads(data)
    assert result == expected
