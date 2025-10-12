import pytest

from hocon import load
from pathlib import Path

@pytest.mark.xfail
def test_1():
    conf_filepath = Path(__file__).parent / "data" / "main.conf"
    result = load(open(conf_filepath))
    print(result)