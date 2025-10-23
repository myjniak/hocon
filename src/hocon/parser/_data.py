from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ParserInput:
    data: str
    absolute_filepath: str | Path
    root_path: list[str] = field(default_factory=list)
    encoding: str = "UTF-8"

    def __getitem__(self, item: slice | int) -> str:
        return self.data.__getitem__(item)
