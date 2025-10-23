from pathlib import Path

from hocon.__version__ import __version__


def test_changelog():
    assert __version__ in Path("CHANGELOG.md").read_text(), f"version {__version__} not documented in CHANGELOG.md file!"
