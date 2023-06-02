import dataclasses
from collections import defaultdict
from operator import itemgetter
from typing import Dict, Set, Tuple

from . import TextProvider, TextProviderArgs, CannotGenerateText, random_word_len

import random


@dataclasses.dataclass
class TextStatistics:
    """
    Scheiß klasse, weg damit
    """
    twograms: Dict[str, int]
    char_count: Dict[str, int]
    allowed_chars: Set[str]


class CharProbTable:
    """
    Stellt eine "Tabelle" dar, weche speicher, welcher buchstabe nach welchem wie wahrscheinlich kommen kann.
    Bietet ein paar Funktionen, um "Spalten" und "Zeilen" bzw Einträge zu löschen.
    """
    table: Dict[str, Dict[str, float]]

    def __init__(self, table):
        self.table = table

    @classmethod
    def from_twograms(cls, twograms: Dict[str, int]):
        """
        Kreiert ein CharProbTable aus einem dict aus twograms und deren Anzahl
        :param twograms:
        :return:
        """
        char_counts = defaultdict(int)
        for (c, _), count in twograms.items():
            char_counts[c] += count

        table = defaultdict(dict)

        for (c1, c2), count in twograms.items():
            table[c1][c2] = count / char_counts[c1]

        return CharProbTable(table)

    def rand_followup_char(self, char):
        """
        Wählt einen zufälligen Buchstaben basierend auf einem Vorgängerbuchstabe. Wahrscheinlichere Buchstaben werden
        eher gewählt.
        :param char: Vorgängerbuchstabe
        :return: ein Buchstabe, der nach dem Vorgängerbuchstabe folgt (zufällig ausgewählt)
        :raises KeyError: wenn auf den Buchstaben kein anderer folgen kann
        """
        choices = list(self.table[char].items())
        if not choices:
            raise KeyError(char)
        index = select_random(map(itemgetter(1), choices))
        return choices[index][0]

    def _recalc_probs(self):
        for c, table in self.table.items():
            s = sum(table.values())
            self.table[c] = {c: p / s for c, p in table.items()}


    def retain(self, pred):
        """
        Ein Prädikat f(a, b) -> bool gibt an, welche buchstabenpaare behalten werden sollen. Erstellt eine neue Tabelle,
        bei welcher nur die gefilterten buchstabenpaare übrig bleiben. Sinnvoll, wenn eine eingeschränkte menge von
        Buchstaben für Buchstabengenerierung verwendet werden soll
        :param pred: DAs Prädikat. Ein efuntkion, die 2 argumente annimmt
        :return: eine neue Tabelle/CharProbTable
        """
        new_table = {}
        for c1, table_ in self.table.items():
            new_table_ = {}
            for c2, p in table_.items():
                if not pred(c1, c2):
                    continue
                new_table_[c2] = p
            new_table[c1] = new_table_

        cpt = CharProbTable(new_table)
        cpt._recalc_probs()
        return cpt




def select_random(probs, total=1.0):
    """
    Wählt zufällig ein element (den index davon) aus einem iterator aus flaots aus. "total" gibt die summe der floats in
    probs an. Ist sie anders als
    :param probs: eine Aufzählung von wahrscheinlichkeiten
    :param total: Die summe der Wahrscheinlichkeiten, standartmäßig 1
    :return: ein zufälliger Index. Indices sind entsprechend den Wahrscheinlichkeiten verteilt
    """
    x = random.random() * total
    acc = 0
    for i, p in enumerate(probs):
        acc += p
        if x < acc:
            return i
    raise Exception


class StatisticalTextProvider(TextProvider):
    """
    Ein Textgenerator, welcher Text auf basis von Buchstabenpaaren und deren Wahrscheinlichkeiten generiert. Falls keine
    Wahrscheinlichkeitsdaten vorhanden sind, werden Buchstaben zufällig ausgewählt.
    """

    def __init__(self, char_probs: TextStatistics):
        """
        Kreiert ein Objekt dieser Klasse auf basis eines TextStatistics objektes (erstellbar und speicherbar s.
        tools/text_statistics.py)
        :param char_probs: TextStatistics
        """
        self.table = CharProbTable.from_twograms(char_probs.twograms)

    @classmethod
    def from_pickle(cls, path):
        """
        Kreiert ein Objekt auf basis eines Pfades zu einem Pickle-Objekt, welches ein TextStatistics-Objekt enthält.
        Macht alles ein bisschen einfacher.
        :param path: Der pfad zu einer Pickle-Datei
        :return: StatisticalTextProvider
        """
        import pickle
        char_probs = pickle.load(open(path, "rb"))
        return cls(char_probs)

    def generate_word(self, table, chars):
        """
        Generiert ein Wort auf basis eines CharProbTable (table) und den allgemein erlaubten buchstaben (chars)
        :return: ein Generiertes wort
        """
        current = " "
        target_len = random_word_len()
        acc = ""
        for _ in range(target_len):
            try:
                next = table.rand_followup_char(current)
            except KeyError:
                next = random.choice(chars)
            acc += next
            current = next

        return acc

    def get_text(self, args: TextProviderArgs):
        """
        Generiert einen Text mit einer länge zwischen args.min_length und args.max_length und Wörtern, welche aus
        args.chars bestehen. Buchstabenwahl hängt vom vorangegangen Buchstaben ab.
        :param args: Generator-Argumente
        :return: einen String, der möglichst wie ein "normaler" text aussieht, aber trotzdem generiert wird und args
        gerecht wird.
        """
        try:
            table = self.table.retain(lambda c1, c2: (c1 in args.chars or c1 == " ") and c2 in args.chars)

            target_len = random.randint(args.min_length, args.max_length)

            acc = ""
            while len(acc) < target_len:
                acc += self.generate_word(table, args.chars) + " "
            if len(acc) > args.max_length:
                acc = acc[:args.max_length]
            return acc.rstrip()
        except KeyError:
            raise CannotGenerateText(f"Unable to generate text with chars {args.chars!r}, available are {''.join(sorted(self.table.table.keys())).strip()!r}")
