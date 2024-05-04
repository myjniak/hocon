import pytest

import hocon

pytestmark = pytest.mark.f12


@pytest.mark.xfail
def test_key_starting_with_include():
    """As a special rule, the unquoted string include may not begin a path expression in a key,
    because it has a special interpretation"""
    data = """
    include.me = 1
    """
    with pytest.raises(Exception):
        hocon.loads(data)
