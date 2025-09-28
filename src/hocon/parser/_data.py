import os
from dataclasses import dataclass
from typing import Optional


@dataclass
class ParserInput:
    data: str
    absolute_filepath: str | os.PathLike
    root_path: Optional[list[str]] = None

    def __post_init__(self):
        if self.root_path is None:
            self.root_path = []

    def __getitem__(self, item):
        return self.data.__getitem__(item)
