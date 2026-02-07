"""Useful for customized parsing."""

from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParserInput:
    """Represents parsing input (data + metadata)."""

    data: str
    absolute_filepath: str | Path
    root_path: list[str] = field(default_factory=list)
    encoding: str = "UTF-8"

    def __getitem__(self, item: slice | int) -> str:
        """Return data slice."""
        return self.data.__getitem__(item)
