import re
from typing import Any

WHITE_HEXES = [
    0x00A0,
    0x1680,
    0x2000,
    0x2001,
    0x2002,
    0x2003,
    0x2004,
    0x2005,
    0x2006,
    0x2007,
    0x2008,
    0x2009,
    0x200A,
    0x202F,
    0x205F,
    0x3000,
    0xFEFF,
    0x001C,
    0x001D,
    0x001E,
    0x001F,
    0x2028,
    0x2029,
]
INLINE_WHITE_CHARS = " \t\r\v\f" + "".join(map(chr, WHITE_HEXES))
WHITE_CHARS: str = INLINE_WHITE_CHARS + "\n"
UNQUOTED_STR_FORBIDDEN_CHARS = '$"{}[]:=,+#`^?!@*&\\'
_FLOAT_CONSTANTS = {
    "-Infinity": float("-inf"),
    "Infinity": float("inf"),
    "NaN": float("nan"),
}
NUMBER_RE = re.compile(r"(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?", (re.VERBOSE | re.MULTILINE | re.DOTALL))
ELEMENT_SEPARATORS = ",\n"
SECTION_OPENING = "{["
SECTION_CLOSING = "}]"

SIMPLE_VALUE_TYPE = int | float | str | bool | None
ANY_VALUE_TYPE = dict[Any, Any] | list[Any] | int | float | str | bool | None
ROOT_TYPE = list[Any] | dict[Any, Any]


class Undefined:
    pass


UNDEFINED = Undefined()
