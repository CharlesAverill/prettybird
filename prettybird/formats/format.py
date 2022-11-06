from abc import ABC, abstractmethod

from ..symbol import Symbol

from typing import List

import warnings


class Format(ABC):
    def __init__(self, filename: str, font_name: str, version: str):
        file_suffix = "." + type(self).__name__.lower()
        if not filename:
            filename = font_name + file_suffix
        elif not filename.lower().endswith(file_suffix):
            warnings.warn(f'{type(self).__name__} files should end with "{file_suffix}"', UserWarning)

        self.filename = filename
        self.font_name = font_name
        self.version = version
        self.symbols: List[Symbol] = []

    def add_symbols(self, symbols: list[Symbol]):
        self.symbols = symbols

    @abstractmethod
    def compile(self, to_ttf=False, bitmap=False, save=True):
        pass
