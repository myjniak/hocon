class HOCONDecodeError(Exception):
    ...


class HOCONNoDataError(HOCONDecodeError):
    """In case there is no data"""
