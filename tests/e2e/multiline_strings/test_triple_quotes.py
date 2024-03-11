from pathlib import Path

import pytest

import hocon

pytestmark = pytest.mark.f9


def test_unicode():
    """If the three-character sequence \"\"\" appears, then all Unicode characters until a closing \"\"\" sequence
    are used unmodified to create a string value."""
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
    any sequence of at least three quotes ends the multi-line string, and any "extra" quotes are part of the string."""
    data_filepath = Path(__file__).parent / "data" / "multiquotes.hocon"
    result = hocon.loads(data_filepath.read_text(encoding="UTF-8"))
    assert result == ["foo\"", "\"foo\"\"\"\"\""]
