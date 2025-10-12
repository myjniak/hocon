class HOCONError(Exception):
    """Generic HOCON library error"""


class HOCONDecodeError(HOCONError):
    """Generic error when parsing HOCON"""


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


class HOCONIncludeError(HOCONDecodeError):
    """when include feature is used in an unsupported way."""


class HOCONResolveError(HOCONError):
    """Generic HOCON resolve error"""


class HOCONConcatenationError(HOCONResolveError):
    """When unsupported concatenation happens"""


class HOCONDeduplicationError(HOCONResolveError):
    """When key duplication resolving fails"""


class HOCONDuplicateKeyMergeError(HOCONDeduplicationError):
    """When duplicated keys cannot be merged"""


class HOCONSubstitutionError(HOCONResolveError):
    """Generic substitution Error"""


class HOCONSubstitutionUndefinedError(HOCONSubstitutionError):
    """When a substitution of ${} could not be resolved in the document or external sources"""


class HOCONSubstitutionCycleError(HOCONSubstitutionError):
    """When a cycle of ${} references is detected"""
