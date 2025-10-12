from dataclasses import dataclass, field
from itertools import count
from typing import Optional, Type, Union, Any

from typing_extensions import Self

from hocon.constants import SIMPLE_VALUE_TYPE, UNDEFINED
from hocon.exceptions import HOCONConcatenationError
from hocon.strings import UnquotedString


class UnresolvedConcatenation(list):

    def __repr__(self):
        list_str = super().__repr__()
        return "\n〈" + list_str[1:-1].replace("\n", "\n    ") + "〉\n"

    def get_type(self) -> Type[list | dict | str]:
        concat_types = set(type(value) for value in self)
        concat_types.discard(UnresolvedSubstitution)
        if all(issubclass(concat_type, SIMPLE_VALUE_TYPE) for concat_type in concat_types):
            return str
        if len(concat_types) > 1:
            type_names = [concat_type.__name__ for concat_type in concat_types]
            raise HOCONConcatenationError(f"Multiple types concatenation not allowed: {type_names}")
        return concat_types.pop()

    def has_substitutions(self) -> bool:
        concat_types = set(type(value) for value in self)
        return UnresolvedSubstitution in concat_types

    def sanitize(self) -> Self:
        concatenation = self._filter_out_undefined_substitutions()
        if any(isinstance(value, (list, dict)) for value in concatenation):
            concatenation = concatenation.filter_out_unquoted_space()
        elif any(isinstance(value, str) for value in concatenation):
            concatenation = concatenation._strip_unquoted_space()
        concatenation.get_type()
        return concatenation

    def filter_out_unquoted_space(self) -> Self:
        return UnresolvedConcatenation(filter(lambda v: not self._is_empty_unquoted_string(v), self))

    def _filter_out_undefined_substitutions(self) -> Self:
        return UnresolvedConcatenation(filter(lambda v: v is not UNDEFINED, self))

    def _strip_unquoted_space(self) -> Self:
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


class UnresolvedDuplicateValue(list):
    def __repr__(self):
        list_str = super().__repr__()
        return "\n【\n" + list_str[1:-1].replace("\n", "\n    ") + "\n】\n"


@dataclass
class UnresolvedSubstitution:
    keys: list[str]
    optional: bool
    relative_location: Optional[list[str]] = None
    including_root: Optional[list[str]] = None
    id_: int = field(default_factory=count().__next__)

    def __post_init__(self):
        if self.including_root is None:
            self.including_root = []
        if self.relative_location is None:
            self.relative_location = []

    @property
    def location(self):
        return self.including_root + self.relative_location

    def __str__(self):
        return r"${" + ("?" if self.optional else "") + ".".join(self.keys) + r"}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other: object):
        if not isinstance(other, UnresolvedSubstitution):
            return NotImplemented
        return self.keys == other.keys and self.optional == other.optional

    def __hash__(self):
        return hash((".".join(self.keys), self.optional, self.location, self.id_))


ANY_UNRESOLVED = Union[UnresolvedConcatenation, UnresolvedSubstitution, UnresolvedDuplicateValue]
