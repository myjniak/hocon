import pytest

from hocon.constants import UNDEFINED
from hocon.exceptions import HOCONConcatenationError
from hocon.resolver import _lazy_resolver
from hocon.unresolved import UnresolvedConcatenation


def test_lazy_resolve_unsupported_type():
    with pytest.raises(NotImplementedError):
        _lazy_resolver.resolve({1, 2, 3})


def test_resolve_empty_concatenation():
    concatenation = UnresolvedConcatenation([])
    resolved = _lazy_resolver.resolve(concatenation)
    assert resolved == UNDEFINED


def test_concatenation_cant_contain_unsupported_hocon_types():
    concatenation = UnresolvedConcatenation([{5}, {4, 3}])
    with pytest.raises(HOCONConcatenationError, match="Concatenation of type set not supported!"):
        _lazy_resolver.resolve(concatenation)


def test_concatenation_cant_contain_concatenations():
    concatenation = UnresolvedConcatenation([UnresolvedConcatenation([5])])
    with pytest.raises(HOCONConcatenationError, match="Concatenation of type UnresolvedConcatenation not supported!"):
        _lazy_resolver.resolve(concatenation)


def test_cant_merge_unsupported_types():
    with pytest.raises(NotImplementedError):
        _lazy_resolver.merge_dict_concatenation({1,2,3}, {4:5})


def test_resolve_multiple_simple_type_concatentation():
    """At the point of resolving unresolved simple concatenations should only consist of strings"""
    concatenation = UnresolvedConcatenation([True, 6, None, "fun"])
    with pytest.raises(HOCONConcatenationError, match="Lazy concatenation of types .* not allowed."):
        _lazy_resolver.resolve(concatenation)
