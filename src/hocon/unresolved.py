from dataclasses import dataclass, field
from itertools import count
from typing import Any, Self, get_args

from hocon.constants import SIMPLE_VALUE_TYPE, UNDEFINED
from hocon.exceptions import HOCONConcatenationError, HOCONDuplicateKeyMergeError
from hocon.strings import UnquotedString


class UnresolvedConcatenation(list):

    def __repr__(self) -> str:
        return "〈" + super().__repr__()[1:-1] + "〉"

    def get_type(self) -> type[list[Any] | dict[Any, Any] | str]:
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
        if concat_type not in [list, dict]:
            msg = f"Concatenation of type {concat_type.__name__} not supported!"
            raise HOCONConcatenationError(msg)
        return concat_type

    def has_substitutions(self) -> bool:
        concat_types = {type(value) for value in self}
        return UnresolvedSubstitution in concat_types

    def sanitize(self) -> Self:
        concatenation = self._filter_out_undefined_substitutions()
        if any(type(value) in [list, dict] for value in concatenation):
            concatenation = concatenation.filter_out_unquoted_space()
        elif any(isinstance(value, str) for value in concatenation):
            concatenation = concatenation.strip_unquoted_space()
        concatenation.get_type()
        return concatenation

    def filter_out_unquoted_space(self) -> Self:
        return UnresolvedConcatenation(filter(lambda v: not self._is_empty_unquoted_string(v), self))

    def _filter_out_undefined_substitutions(self) -> Self:
        return UnresolvedConcatenation(filter(lambda v: v is not UNDEFINED, self))

    def strip_unquoted_space(self) -> Self:
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
    def _is_empty_unquoted_string(value: Any) -> bool:
        return isinstance(value, UnquotedString) and value.is_empty()


class UnresolvedDuplication(list):
    def __repr__(self) -> str:
        return "【" + super().__repr__()[1:-1] + "】"

    def sanitize(self) -> Self:
        if len(self) == 0:
            msg = "Unresolved duplicate key must contain at least 2 elements."
            raise HOCONDuplicateKeyMergeError(msg)
        for index in reversed(range(len(self))):
            if not isinstance(self[index], dict | ANY_UNRESOLVED):
                return UnresolvedDuplication([*self[index + 1 :]])
        return self


@dataclass
class UnresolvedSubstitution:
    keys: list[str]
    optional: bool
    relative_location: list[str] = field(default_factory=list)
    including_root: list[str] = field(default_factory=list)
    id_: int = field(default_factory=count().__next__)

    @property
    def location(self) -> list[str]:
        return self.including_root + self.relative_location

    def __str__(self) -> str:
        return r"${" + ("?" if self.optional else "") + ".".join(self.keys) + r"}"

    def __repr__(self) -> str:
        return self.__str__()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, UnresolvedSubstitution):
            return NotImplemented
        return self.keys == other.keys and self.optional == other.optional and self.location == other.location

    def __hash__(self) -> int:
        return hash((".".join(self.keys), self.optional, ".".join(self.location)))


ANY_UNRESOLVED = UnresolvedConcatenation | UnresolvedSubstitution | UnresolvedDuplication
