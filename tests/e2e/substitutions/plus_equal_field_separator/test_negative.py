import pytest

import hocon
from hocon.exceptions import HOCONConcatenationError

pytestmark = pytest.mark.f13_2


def test_iadd_non_array():
    """If the previous value was not an array, an error will result
    just as it would in the long form a = ${?a} [3]"""
    data = """
    a = 12
    a += 3
    """
    with pytest.raises(HOCONConcatenationError, match="Concatenation of multiple types"):
        hocon.loads(data)
