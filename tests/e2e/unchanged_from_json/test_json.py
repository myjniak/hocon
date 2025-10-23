"""All valid JSON should be valid and should result in the same in-memory data that a JSON parser would have produced.
quoted strings are in the same format as JSON strings
values have possible types: string_, number, object, array, boolean, null
"""
import json
from pathlib import Path

import pytest

import hocon


@pytest.mark.f1
@pytest.mark.parametrize("filename", [
    "special_chars.json",
    "nested.json",
    "empty.json",
    "emptier.json",
    "emptier2.json",
])
def test_json_loads(filename: str):
    data = (Path(__file__).parent / "data" / filename).read_text()
    loaded_hocon = hocon.loads(data)
    loaded_json = json.loads(data)
    assert loaded_json == loaded_hocon
