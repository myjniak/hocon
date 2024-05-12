from pathlib import Path

import pytest

import hocon

pytestmark = pytest.mark.f14


def test_basic():
    conf_filepath = Path(__file__).parent / "data" / "basic" / "application.conf"
    result = hocon.load(open(conf_filepath))
    print(result)
