import pytest

from hocon.constants import UNDEFINED
from hocon.exceptions import HOCONDeduplicationError, HOCONConcatenationError
from hocon.resolver._resolver import Resolver
from hocon.unresolved import UnresolvedConcatenation, UnresolvedDuplication


def test_resolve_unsupported_type():
    with pytest.raises(NotImplementedError):
        Resolver({}).resolve({1, 2, 3})


def test_resolve_single_element_concatenation():
    concatenation = UnresolvedConcatenation([5])
    resolved = Resolver({}).resolve(concatenation)
    assert resolved == 5


def test_resolve_empty_concatenation():
    concatenation = UnresolvedConcatenation([])
    resolved = Resolver({}).resolve(concatenation)
    assert resolved == UNDEFINED


def test_resolve_duplication_with_no_elements():
    duplication = UnresolvedDuplication([])
    with pytest.raises(HOCONDeduplicationError):
        Resolver({}).resolve(duplication)


def test_concatenation_cant_contain_concatenations():
    concatenation = UnresolvedConcatenation([UnresolvedConcatenation([5])])
    with pytest.raises(HOCONConcatenationError):
        Resolver({}).resolve(concatenation)
