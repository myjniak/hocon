import re
from typing import Union

WHITE_HEXES = [0x00A0, 0x2007, 0x202F, 0xFEFF, 0x001C, 0x001D, 0x001E, 0x001F]
INLINE_WHITE_CHARS = " \t\r\v\f" + "".join(map(chr, WHITE_HEXES))
WHITE_CHARS: str = INLINE_WHITE_CHARS + "\n"
KEY_VALUE_SEPARATORS = ":="
UNQUOTED_STR_FORBIDDEN_CHARS = '$"{}[]:=,+#`^?!@*&\\'
_FLOAT_CONSTANTS = {
    '-Infinity': float('-inf'),
    'Infinity': float('inf'),
    'NaN': float('nan'),
}
NUMBER_RE = re.compile(
    r'(-?(?:0|[1-9]\d*))(\.\d+)?([eE][-+]?\d+)?',
    (re.VERBOSE | re.MULTILINE | re.DOTALL))
ELEMENT_SEPARATORS = ",\n"
SECTION_CLOSURES = "}]"

SIMPLE_VALUE_TYPE = Union[int, float, str, bool, None]
ANY_VALUE_TYPE = Union[dict, list, int, float, str, bool, None]
