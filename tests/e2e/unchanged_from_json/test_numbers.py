"""allowed number formats matches JSON; as in JSON, some possible floating-point
values are not represented, such as NaN
"""
import json
import math

import pytest

import hocon

pytestmark = pytest.mark.f1


def test_float():
    result = hocon.loads("a: NaN")
    assert math.isnan(result["a"])


def test_inf():
    result = hocon.loads("a: -Infinity")
    assert math.isinf(result["a"])
    result = hocon.loads("a: Infinity")
    assert math.isinf(result["a"])


def test_large_int():
    large_int = "[9223372036854775808654132]"
    assert hocon.loads(large_int) == json.loads(large_int)


def test_large_float():
    large_float = "[9223372036854775808654132.63463643673645]"
    assert hocon.loads(large_float) == json.loads(large_float)
