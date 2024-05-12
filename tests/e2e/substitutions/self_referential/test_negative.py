"""
An object or array with a substitution inside it is not considered self-referential for this purpose.
"""

import hocon
import pytest

from hocon.exceptions import HOCONSubstitutionCycleError, HOCONSubstitutionUndefinedError


def test_unbreakable_cycle_dict():
    data = """
    a: a
    a : { b : ${a} }
    """
    with pytest.raises(HOCONSubstitutionCycleError, match=r"\$\{a\}.*a\.b"):
        hocon.loads(data)


def test_unbreakable_cycle_list():
    data = """a : [${a}]"""
    with pytest.raises(HOCONSubstitutionCycleError, match=r"\$\{a\}.*a\.0"):
        hocon.loads(data)


def test_circular_reference_missing():
    data = """a : ${a}"""
    with pytest.raises(HOCONSubstitutionUndefinedError):
        hocon.loads(data)
