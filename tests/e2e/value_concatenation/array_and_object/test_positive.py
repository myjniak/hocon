"""Within a field value or array element,
if only non-newline whitespace separates the end of a first array or object or substitution
from the start of a second array or object or substitution,
the two values are concatenated.\
Newlines may occur within the array or object, but not between them.
Newlines between prevent concatenation.
"""
import pytest

import hocon

pytestmark = pytest.mark.f10_2


def test_object_concatenation():
    """For objects, "concatenation" means "merging", so the second object overrides the first."""
    data = """
    // one object
    a : { b : 1, c : 2 }  
    """
    data_2 = """
    // two objects that are merged via concatenation rules
    a : { b : 1 } { c : 2 }
    """
    data_3 = """
    // two fields that are merged
    a : { b : 1 }
    a : { c : 2 }
    """
    assert hocon.loads(data) == hocon.loads(data_2) == hocon.loads(data_3) == {"a": {"b": 1, "c": 2}}


def test_array_concatenation():
    data = """
    // one array
    a : [ 1, 2, 3, 4 ]
    """
    data_2 = """
    // two arrays that are concatenated
    a : [ 1, 2 ] [ 3, 4 ]
    """
    data_3 = """
    // a later definition referring to an earlier
    // (see "self-referential substitutions" below)
    a : [ 1, 2 ]
    a : ${a} [ 3, 4 ]
    """
    assert hocon.loads(data) == hocon.loads(data_2) == hocon.loads(data_3) == {"a": [1, 2, 3, 4]}


def test_array_deduplication():
    data = """
    a : [ 1, 2, 3, 4 ]
    // second array should override the first one
    a : [ 5, 6 ] [ 7, 8 ]
    """
    assert hocon.loads(data) == {"a": [5, 6, 7, 8]}



def test_inheritance():
    data = """
    data-center-generic = { cluster-size = 6 }
    data-center-east = ${data-center-generic} { name = "east" }
    """
    assert hocon.loads(data) == {
        "data-center-generic": {"cluster-size": 6},
        "data-center-east": {"cluster-size": 6, "name": "east"},
    }


def test_add_paths():
    data = """
    path = [ /bin ]
    path = ${path} [ /usr/bin ]
    """
    assert hocon.loads(data) == {"path": ["/bin", "/usr/bin"]}
