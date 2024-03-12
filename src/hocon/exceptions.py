class HOCONDecodeError(Exception):
    ...


class HOCONNoDataError(HOCONDecodeError):
    """In case there is no data"""


class HOCONExcessiveDataError(HOCONDecodeError):
    """In case HOCON braces have closed the whole structure but there's still unparsed data remaining."""


class HOCONUnexpectedBracesError(HOCONDecodeError):
    """When an unexpected closure happens."""


class HOCONUnexpectedSeparatorError(HOCONDecodeError):
    """When an unexpected comma happens."""


class HOCONUnquotedStringError(HOCONDecodeError):
    """When forbidden character is used within an unquoted string"""


class HOCONInvalidKeyError(HOCONDecodeError):
    """Objects and arrays do not make sense as field keys."""
