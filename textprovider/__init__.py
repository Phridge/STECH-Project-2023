import abc
import dataclasses
from typing import Set
from enum import Enum


@dataclasses.dataclass
class TextProviderArgs:
    min_length: int
    max_length: int
    chars: str
    length_factor: float = 1.0



class Charset(str, Enum):
    ALPHA = "abcdefghijklmnopqrstuvwxyzäöüß"
    UPPER = ALPHA.upper()
    NUMBERS = "1234567890"
    EASY_PUNCT = ".,-;:?!"
    ALL_PUNCT = ",.-!\"§$%&/()=?^#+;:_*'~°´`€@[]{}\\<>|"
    EVERYTHING = ALPHA + UPPER + NUMBERS + ALL_PUNCT



class CannotGenerateText(Exception):
    pass


class TextProvider(abc.ABC):
    def get_text(self, args: TextProviderArgs):
        raise NotImplementedError