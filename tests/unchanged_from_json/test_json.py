import json
from pathlib import Path

import hocon
import pytest


@pytest.mark.f1
@pytest.mark.parametrize("filename", [
    "special_chars.json",
    "nested.json",
    "empty.json"
])
def test_json_loads(filename: str):
    data = (Path(__file__).parent / "data" / filename).read_text()
    loaded_hocon = hocon.loads(data)
    loaded_json = json.loads(data)
    assert loaded_json == loaded_hocon
