import pytest

import hocon
from hocon.exceptions import HOCONSubstitutionUndefinedError

pytestmark = pytest.mark.f13


@pytest.mark.xfail
def test_undefined():
    data = "key: ${i_dont_exist}"
    with pytest.raises(HOCONSubstitutionUndefinedError):
        hocon.loads(data)
