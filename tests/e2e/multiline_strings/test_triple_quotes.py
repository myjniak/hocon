from pathlib import Path

import pytest

import hocon

pytestmark = pytest.mark.f9


def test_unicode():
    """If the three-character sequence \"\"\" appears, then all Unicode characters until a closing \"\"\" sequence
    are used unmodified to create a string_ value."""
    data_filepath = Path(__file__).parent / "data" / "unicode.hocon"
    result = hocon.loads(data_filepath.read_text(encoding="UTF-8"))
    assert result == ["""'$"{[]:=+#^?!@*&\n    안녕하세요\n    """]


def test_unicode_escapes():
    """Unicode escapes are not interpreted in triple-quoted strings."""
    data_filepath = Path(__file__).parent / "data" / "escapes.hocon"
    result = hocon.loads(data_filepath.read_text(encoding="UTF-8"))
    assert result == [r"\n\'\t"]


def test_multiquotes():
    """HOCON works like Scala:
    any sequence of at least three quotes ends the multi-line string_, and any "extra" quotes are part of the string_."""
    data_filepath = Path(__file__).parent / "data" / "multiquotes.hocon"
    result = hocon.loads(data_filepath.read_text(encoding="UTF-8"))
    assert result == ["foo\"", "\"foo\"\"\"\"\""]


def test_in_all_supported_places():
    """In keys, values and list elements"""
    data_filepath = Path(__file__).parent / "data" / "triplequotes_everywhere.hocon"
    result = hocon.loads(data_filepath.read_text(encoding="UTF-8"))
    assert result == [{"this is\n a key": "This is a\nvalue"}, 1, " list element "]
