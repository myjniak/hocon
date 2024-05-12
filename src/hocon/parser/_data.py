import os
from dataclasses import dataclass


@dataclass
class ParserInput:
    data: str
    absolute_filepath: str | os.PathLike

    def __getitem__(self, item):
        return self.data.__getitem__(item)
