from pathlib import Path

import pytest

import hocon

pytestmark = pytest.mark.f14_3


def test_two_different_paths():
    """Substitutions in included files are looked up at two different paths;
    first, relative to the root of the included file;
    second, relative to the root of the including configuration."""
    conf_filepath = Path(__file__).parent / "data" / "root.conf"
    result = hocon.load(open(conf_filepath))
    assert result == {"a": {"x": 10, "y": 10, "z": 10}}


def test_root_redefinition():
    """Substitution happens after parsing the whole configuration."""
    conf_filepath = Path(__file__).parent / "data" / "root2.conf"
    result = hocon.load(open(conf_filepath))
    assert result == {"a": {"x": 42, "y": 42, "z": 42}}
