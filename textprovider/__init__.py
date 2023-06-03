import abc
import dataclasses
import random
from typing import Set
from enum import Enum


@dataclasses.dataclass
class TextProviderArgs:
    """
    Klasse, die die argumente für einen Text Provider (Generator) zusammenfasst.
    min_length: untergrenze der textlänge
    max_length: obergrenze der textlänge
    chars: string, der alle im text erlaubten buchstaben enthölt
    length_factor: relative länge der generierten worte. Länge = ~5 * length_factor
    """
    min_length: int
    max_length: int
    chars: str
    length_factor: float = 1.0



class Charset(str, Enum):
    """
    Schnellauswahl für Buchstabengruppen
    """
    ALPHA = "abcdefghijklmnopqrstuvwxyzäöüß"
    UPPER = ALPHA.upper()
    NUMBERS = "1234567890"
    ALNUM = ALPHA + UPPER + NUMBERS
    EASY_PUNCT = ".,-;:?!"
    ALL_PUNCT = ",.-!\"§$%&/()=?^#+;:_*'~°´`€@[]{}\\<>|"
    EVERYTHING = ALPHA + UPPER + NUMBERS + ALL_PUNCT

ALL_CHARSETS = (
    Charset.ALPHA,
    Charset.UPPER,
    Charset.NUMBERS,
    Charset.EASY_PUNCT,
    Charset.ALL_PUNCT,
)



class CannotGenerateText(Exception):
    """
    Wird geworfen, wenn ein Generator keinen Text unter den gegebenen einschränkungen generieren kann.
    """
    pass


class TextProvider(abc.ABC):
    """
    Abstrakter Text Provider (Generator). Generiert Text.
    """
    def get_text(self, args: TextProviderArgs):
        """
        Generiere text unter den gegebenen Einschränkungen.
        :param args: Einschränkungen
        :return: Text
        :raises CannnotGenerateText: wenn kein Text generiert werden konnte
        """
        raise NotImplementedError


def random_word_len(factor=1.0):
    """
    Generiert zufällige Wortlänge.
    :param factor: längenfaktor
    :return:
    """
    return int(factor * random.triangular(3, 11 * factor, 5 * factor))

