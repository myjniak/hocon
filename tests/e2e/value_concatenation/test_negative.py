"""Objects and arrays do not make sense as field keys."""
import pytest

import hocon
from hocon.exceptions import HOCONInvalidKeyError

pytestmark = pytest.mark.f10


def test_list_as_key():
    with pytest.raises(HOCONInvalidKeyError, match="Objects and arrays do not make sense as field keys."):
        hocon.loads("{[]: value}")


def test_dict_as_key():
    with pytest.raises(HOCONInvalidKeyError, match="Objects and arrays do not make sense as field keys."):
        hocon.loads("{{}: value}")
