"""WHITESPACE is:
- any Unicode space separator (Zs category), line separator (Zl category),
or paragraph separator (Zp category),
including nonbreaking spaces (such as 0x00A0, 0x2007, and 0x202F).
The BOM (0xFEFF) must also be treated as whitespace.
- tab (\t 0x0009), newline ('\n' 0x000A), vertical tab ('\v' 0x000B),
form feed (\f' 0x000C), carriage return ('\r' 0x000D), file separator (0x001C),
group separator (0x001D), record separator (0x001E), unit separator (0x001F)."""

import pytest

import hocon

pytestmark = pytest.mark.f6


def test_different_chars_as_whitespace():
    data = """a               　﻿  \v\t:   \v\t1
       \v\tb:2
    c:[ 1               　﻿  ,  2, 
    3\v\t]   \v\t[4,5]
    """
    result = hocon.loads(data)
    assert result == {"a": 1, "b": 2, "c": [1, 2, 3, 4, 5]}
