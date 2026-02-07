"""Hocon Exceptions."""

from hocon.parser.data import ParserInput


class HOCONError(Exception):
    """Generic HOCON library error."""

    def __init__(self, message: str, data: ParserInput | None = None, idx: int | None = None) -> None:
        """Include line and column info, print the whole problematic line, if not empty."""
        self.location = ""
        self.line = ""
        if data and idx:
            self.location, self.line = self._prepare_message_suffix(data, idx)
        self.message = message
        final_msg = self.message + ": " + self.location + "\n" + self.line.strip("\n")
        super().__init__(final_msg)

    @staticmethod
    def _prepare_message_suffix(data: ParserInput, idx: int) -> tuple[str, str]:
        data_up_to_idx = data.data[:idx]
        line_no = data_up_to_idx.count("\n") + 1
        idx_line_beginning = data_up_to_idx.rfind("\n")
        if idx_line_beginning == -1:
            idx_line_beginning = 0
        idx_line_end = data.data.find("\n", idx_line_beginning + 1)
        col = idx - idx_line_beginning
        return f"line {line_no} col {col}", data.data[idx_line_beginning:idx_line_end]


class HOCONDecodeError(HOCONError):
    """Generic error when parsing HOCON."""


class HOCONNoDataError(HOCONDecodeError):
    """In case there is no data."""


class HOCONExcessiveDataError(HOCONDecodeError):
    """In case HOCON braces have closed the whole structure but there's still unparsed data remaining."""


class HOCONUnexpectedBracesError(HOCONDecodeError):
    """When an unexpected closure happens."""


class HOCONUnexpectedSeparatorError(HOCONDecodeError):
    """When an unexpected comma happens."""


class HOCONUnquotedStringError(HOCONDecodeError):
    """When forbidden character is used within an unquoted string."""


class HOCONInvalidKeyError(HOCONDecodeError):
    """Objects and arrays do not make sense as field keys."""


class HOCONIncludeError(HOCONDecodeError):
    """when include feature is used in an unsupported way."""


class HOCONResolveError(HOCONError):
    """Generic HOCON resolve error."""


class HOCONConcatenationError(HOCONResolveError):
    """When unsupported concatenation happens."""


class HOCONDeduplicationError(HOCONResolveError):
    """When key duplication resolving fails."""


class HOCONDuplicateKeyMergeError(HOCONDeduplicationError):
    """When duplicated keys cannot be merged."""


class HOCONSubstitutionError(HOCONResolveError):
    """Generic substitution Error."""


class HOCONSubstitutionUndefinedError(HOCONSubstitutionError):
    """When a substitution of ${} could not be resolved in the document or external sources."""


class HOCONSubstitutionCycleError(HOCONSubstitutionError):
    """When a cycle of ${} references is detected."""
