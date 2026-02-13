import pytest

import hocon
from hocon.exceptions import (
    HOCONSubstitutionCycleError,
    HOCONSubstitutionUndefinedError,
)

pytestmark = pytest.mark.f13_3


def test_circular_reference_missing():
    """In isolation (with no merges involved),
    a self-referential field is an error because the substitution cannot be resolved:
    """
    data = """foo : ${foo} // an error"""
    with pytest.raises(HOCONSubstitutionUndefinedError):
        hocon.loads(data)


def test_bad_order():
    """Here the ${foo} self-reference comes before foo has a value, so it is undefined,
    exactly as if the substitution referenced a path not found in the document.
    Because foo : ${foo} conceptually looks to previous definitions of foo for a value,
    the error should be treated as "undefined" rather than "intractable cycle";
    as a result, the optional substitution syntax ${?foo} does not create a cycle:
    """
    data = """
    foo : ${foo}
    foo : { a : 1 }
    """
    with pytest.raises(HOCONSubstitutionUndefinedError):
        print(hocon.loads(data))


def test_undefined():
    data = """
    a : 1
    b : ${c}
    """
    with pytest.raises(HOCONSubstitutionUndefinedError):
        hocon.loads(data)


def test_impossible_cycle():
    data = """
    bar : ${foo}
    foo : ${bar}"""
    with pytest.raises(HOCONSubstitutionCycleError):
        hocon.loads(data)


def test_impossible_cycle_2():
    data = """
    a : ${b}
    b : ${c}
    c : ${a}"""
    with pytest.raises(HOCONSubstitutionCycleError):
        hocon.loads(data)


def test_undefined_by_spec():
    """Implementations are allowed to handle this by setting both a and b to 1,
    setting both to 2, or generating an error.
    """
    data = """
    a : 1
    b : 2
    a : ${b}
    b : ${a}"""
    assert hocon.loads(data) == {"a": 1, "b": 1}
