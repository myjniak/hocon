import pytest

import hocon
from hocon.exceptions import HOCONConcatenationError, HOCONInvalidKeyError

pytestmark = pytest.mark.f10_2


@pytest.mark.parametrize("data", [
    """{"a": {b:1}[2,3]}""",
    """{"a": [2,3]{b:1}}""",
])
def test_mixed_concatenation(data: str):
    """Arrays can be concatenated with arrays, and objects with objects, but it is an error if they are mixed."""
    with pytest.raises(HOCONConcatenationError):
        hocon.loads(data)


def test_object_as_key():
    """Arrays and objects cannot be field keys, whether concatenation is involved or not."""
    data = "{ [5]: 5 }"
    with pytest.raises(HOCONInvalidKeyError):
        hocon.loads(data)
