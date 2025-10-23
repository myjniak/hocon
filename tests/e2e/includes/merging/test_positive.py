from pathlib import Path

import pytest

import hocon

pytestmark = pytest.mark.f14_2


def test_merging_with_keys_before():
    """If a key in the included object occurred prior to the include statement in the including object,
    the included key's value overrides or merges with the earlier value,
    exactly as with duplicate keys found in a single file.
    """
    conf_filepath = Path(__file__).parent / "data" / "merge_override" / "application.conf"
    result = hocon.load(open(conf_filepath))
    assert result == {
        "a": {"a": 3, "b": 2, "c": 3},
        "b": [0, 0],
    }



def test_merging_with_keys_after():
    """If the including file repeats a key from an earlier-included object,
    the including file's value would override or merge with the one from the included file.
    """
    conf_filepath = Path(__file__).parent / "data" / "merge_overriden" / "application.conf"
    result = hocon.load(open(conf_filepath))
    assert result == {
        "a": {"a": 1, "b": 2, "c": 3},
        "b": 2,
    }
