import pytest

from hocon.constants import UNDEFINED
from hocon.exceptions import HOCONDeduplicationError, HOCONConcatenationError
from hocon.resolver._resolver import Resolver, LazyResolver
from hocon.unresolved import UnresolvedConcatenation, UnresolvedDuplicateValue


def test_resolve_unsupported_type():
    with pytest.raises(NotImplementedError):
        Resolver({}).resolve({1, 2, 3})


def test_lazy_resolve_unsupported_type():
    with pytest.raises(NotImplementedError):
        LazyResolver().resolve({1, 2, 3})


def test_resolve_single_element_concatenation():
    concatenation = UnresolvedConcatenation([5])
    resolved = Resolver({}).resolve_value(concatenation)
    assert resolved == 5


def test_resolve_empty_concatenation():
    concatenation = UnresolvedConcatenation([])
    resolved = Resolver({}).resolve_value(concatenation)
    assert resolved == UNDEFINED
    resolved = LazyResolver().resolve_value(concatenation)
    assert resolved == UNDEFINED


def test_resolve_duplication_with_no_elements():
    duplication = UnresolvedDuplicateValue([])
    with pytest.raises(HOCONDeduplicationError):
        Resolver({}).resolve_value(duplication)


def test_concatenation_cant_contain_unsupported_hocon_types():
    concatenation = UnresolvedConcatenation([{5}, {4, 3}])
    with pytest.raises(HOCONConcatenationError, match="Concatenation of type set not supported!"):
        LazyResolver().concatenate(concatenation)


def test_concatenation_cant_contain_concatenations():
    concatenation = UnresolvedConcatenation([UnresolvedConcatenation([5])])
    with pytest.raises(HOCONConcatenationError):
        Resolver({}).resolve_value(concatenation)
    with pytest.raises(HOCONConcatenationError, match="Concatenation of type UnresolvedConcatenation not supported!"):
        LazyResolver().resolve_value(concatenation)


def test_cant_merge_unsupported_types():
    with pytest.raises(NotImplementedError):
        LazyResolver().merge_dict_concatenation({1,2,3}, {4:5})
