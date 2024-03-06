"""allowed number formats matches JSON; as in JSON, some possible floating-point
values are not represented, such as NaN"""

import math
import pytest
import hocon


@pytest.mark.f1
def test_float():
    result = hocon.loads("a: NaN")
    assert math.isnan(result["a"])


@pytest.mark.f1
def test_inf():
    result = hocon.loads("a: -Infinity")
    assert math.isinf(result["a"])
    result = hocon.loads("a: Infinity")
    assert math.isinf(result["a"])
