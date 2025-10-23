"""Values in arrays, and fields in objects, need not have a comma between them
as long as they have at least one ASCII newline (\n, decimal value 10) between them.

The last element in an array or last field in an object may be followed by a single comma. This extra comma is ignored.
"""
import pytest

import hocon

pytestmark = pytest.mark.f5


def test_values_in_arrays():
    data = """
    [
    1
    2 ,
    3
    4
    5 6 7
    8, 9, 10,
    ]
    """
    result = hocon.loads(data)
    assert result == [1, 2, 3, 4, "5 6 7", 8, 9, 10]


def test_fields_in_dicts():
    data = """
        {
        k1: v1
        k2: v2,
        k3= v3
        k4=v4, k5:v5
        k6=v6, k7:v7,
        }
        """
    result = hocon.loads(data)
    assert result == {
        "k1": "v1",
        "k2": "v2",
        "k3": "v3",
        "k4": "v4",
        "k5": "v5",
        "k6": "v6",
        "k7": "v7",
    }
