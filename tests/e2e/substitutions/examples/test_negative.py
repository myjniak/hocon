import hocon
import pytest

from hocon.exceptions import HOCONSubstitutionUndefinedError, HOCONSubstitutionCycleError


def test_circular_reference_missing():
    data = """foo : ${foo} // an error"""
    with pytest.raises(HOCONSubstitutionUndefinedError):
        hocon.loads(data)


def test_bad_order():
    data = """
    foo : ${foo}
    foo : { a : 1 }
    """
    with pytest.raises(HOCONSubstitutionUndefinedError):
        hocon.loads(data)


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
    setting both to 2, or generating an error."""
    data = """
    a : 1
    b : 2
    a : ${b}
    b : ${a}"""
    result = hocon.loads(data)
    assert result == {
        "a": 1,
        "b": 1
    }
