"""Definition of 3 types unique to hocon, used when resolving parsed data to a simple dict/list."""

from dataclasses import dataclass, field
from itertools import count
from typing import Self, get_args

from hocon.constants import ANY_VALUE_TYPE, SIMPLE_VALUE_TYPE, UNDEFINED
from hocon.exceptions import HOCONConcatenationError, HOCONDuplicateKeyMergeError
from hocon.strings import HOCON_STRING, UnquotedString


class UnresolvedConcatenation(list):
    """A list representing https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#value-concatenation."""

    def __repr__(self) -> str:
        """Replace [] in list repr with 〈 〉 brackets to distinguish Duplications from regular lists, when printed.

        A bare minimum, to be able to represent parsed data as string.
        """
        return "〈" + super().__repr__()[1:-1] + "〉"

    def get_type(self) -> type[list | dict | str]:
        """Scan all concatenation items to evaluate type.

        After all, string concatenations are resolved differently than lists and dicts.
        """
        concat_types = {type(value) for value in self}
        concat_types.discard(UnresolvedSubstitution)
        simple_value_classes = get_args(SIMPLE_VALUE_TYPE)
        if all(issubclass(concat_type, simple_value_classes) for concat_type in concat_types):
            return str
        if len(concat_types) > 1:
            type_names = [concat_type.__name__ for concat_type in concat_types]
            msg = f"Concatenation of multiple types not allowed: {type_names}"
            raise HOCONConcatenationError(msg)
        concat_type = concat_types.pop()
        if concat_type not in {list, dict}:
            msg = f"Concatenation of type {concat_type.__name__} not supported!"
            raise HOCONConcatenationError(msg)
        return concat_type

    def has_substitutions(self) -> bool:
        """Check if ${x} are inside this concatenation."""
        concat_types = {type(value) for value in self}
        return UnresolvedSubstitution in concat_types

    def sanitize(self) -> "UnresolvedConcatenation":
        """Get rid of elements that should be discarded by hocon resolver.

        Raise an exception if self contains elements of multiple types.
        """
        concatenation = self._filter_out_undefined_substitutions()
        if any(type(value) in {list, dict} for value in concatenation):
            concatenation = concatenation.filter_out_unquoted_space()
        elif any(isinstance(value, HOCON_STRING) for value in concatenation):
            concatenation = concatenation.strip_unquoted_space()
        concatenation.get_type()
        return concatenation

    def filter_out_unquoted_space(self) -> "UnresolvedConcatenation":
        """Remove all unquoted spaces from this concatenation."""
        return UnresolvedConcatenation(filter(lambda v: not self._is_empty_unquoted_string(v), self))

    def _filter_out_undefined_substitutions(self) -> "UnresolvedConcatenation":
        return UnresolvedConcatenation(filter(lambda v: v is not UNDEFINED, self))

    def strip_unquoted_space(self) -> "UnresolvedConcatenation":
        """Remove all unquoted spaces from the left and right end of this concatenation."""
        try:
            first = next(index for index, value in enumerate(self) if not self._is_empty_unquoted_string(value))
        except StopIteration:
            return UnresolvedConcatenation([])
        last = -1 * next(
            index for index, value in enumerate(reversed(self)) if not self._is_empty_unquoted_string(value)
        )
        if last == 0:
            return UnresolvedConcatenation(self[first:])
        return UnresolvedConcatenation(self[first:last])

    @staticmethod
    def _is_empty_unquoted_string(value: "ANY_VALUE_TYPE | ANY_UNRESOLVED") -> bool:
        return isinstance(value, UnquotedString) and value.is_empty()


class UnresolvedDuplication(list):
    """A list representing http://github.com/lightbend/config/blob/v1.4.3/HOCON.md#duplicate-keys-and-object-merging."""

    def __repr__(self) -> str:
        """Replace [] in list repr with 【 】 brackets to distinguish Duplications from regular lists, when printed.

        A bare minimum, to be able to represent parsed data as string.
        """
        return "【" + super().__repr__()[1:-1] + "】"

    def sanitize(self) -> Self:
        """Discard all items overriden by a list or a simple value."""
        if len(self) == 0:
            msg = "Unresolved duplicate key must contain at least 2 elements."
            raise HOCONDuplicateKeyMergeError(msg)
        for index in reversed(range(len(self))):
            if not isinstance(self[index], dict | ANY_UNRESOLVED):
                for _ in range(index + 1):
                    del self[0]
                break
        return self


@dataclass
class UnresolvedSubstitution:
    """See https://github.com/lightbend/config/blob/v1.4.3/HOCON.md#substitutions."""

    keys: list[str]
    optional: bool
    relative_location: list[str] = field(default_factory=list)
    including_root: list[str] = field(default_factory=list)
    id_: int = field(default_factory=count().__next__)

    @property
    def location(self) -> list[str]:
        """Return FULL path to this substitution from the very root of the main config file.

        Even if this substitution is defined inside a nested included file.
        """
        return self.including_root + self.relative_location

    def __str__(self) -> str:
        """Reconstruct substitution string from original data, like ${?x}."""
        return r"${" + ("?" if self.optional else "") + ".".join(self.keys) + r"}"

    def __repr__(self) -> str:
        """Return the same str as __str__ for now."""
        return str(self)

    def __eq__(self, other: object) -> bool:
        """Return true when keys, optional flag and location are equal."""
        if not isinstance(other, UnresolvedSubstitution):
            return NotImplemented
        return self.keys == other.keys and self.optional == other.optional and self.location == other.location

    def __hash__(self) -> int:
        """Enable UnresolvedSubstitutions to become ditionary keys for potential user convenience."""
        return hash(self.id_)


ANY_UNRESOLVED = UnresolvedConcatenation | UnresolvedSubstitution | UnresolvedDuplication
