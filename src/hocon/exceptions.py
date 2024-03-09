class HOCONDecodeError(Exception):
    ...


class HOCONNoDataError(HOCONDecodeError):
    """In case there is no data"""


class HOCONExcessiveDataError(HOCONDecodeError):
    """In case HOCON braces have closed the whole structure but there's still unparsed data remaining."""


class HOCONUnexpectedBracesError(HOCONDecodeError):
    """When an unexpected closure happens."""
