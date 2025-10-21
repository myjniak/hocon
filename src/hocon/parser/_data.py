import os
from dataclasses import dataclass, field


@dataclass
class ParserInput:
    data: str
    absolute_filepath: str | os.PathLike
    root_path: list[str] = field(default_factory=list)
    encoding: str = "UTF-8"

    def __getitem__(self, item):
        return self.data.__getitem__(item)
