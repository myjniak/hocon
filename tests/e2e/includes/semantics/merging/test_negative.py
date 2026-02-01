from pathlib import Path

import pytest

import hocon
from hocon.exceptions import HOCONIncludeError

pytestmark = pytest.mark.f14_2


def test_included_file_is_array():
    """An included file must contain an object, not an array. This is significant because both JSON and HOCON allow arrays as root values in a document."""
    conf_filepath = Path(__file__).parent / "data" / "array" / "application.conf"
    with pytest.raises(HOCONIncludeError, match="An included file 'foo.conf' must contain an object, not an array."):
        hocon.load(open(conf_filepath))
