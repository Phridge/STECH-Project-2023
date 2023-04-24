import dataclasses
from collections import defaultdict
from operator import itemgetter
from typing import Dict, Set, Tuple

from . import TextProvider, TextProviderArgs, CannotGenerateText, random_word_len

import random


@dataclasses.dataclass
class TextStatistics:
    twograms: Dict[str, int]
    char_count: Dict[str, int]
    allowed_chars: Set[str]


class CharProbTable:
    table: Dict[str, Dict[str, float]]

    def __init__(self, table):
        self.table = table

    @classmethod
    def from_twograms(cls, twograms: Dict[str, int]):
        char_counts = defaultdict(int)
        for (c, _), count in twograms.items():
            char_counts[c] += count

        table = defaultdict(dict)

        for (c1, c2), count in twograms.items():
            table[c1][c2] = count / char_counts[c1]

        return CharProbTable(table)

    def probs_for(self, char):
        return self.table.get(char, {})

    def rand_followup_char(self, char):
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
    x = random.random() * total
    acc = 0
    for i, p in enumerate(probs):
        acc += p
        if x < acc:
            return i
    raise Exception


class StatisticalTextProvider(TextProvider):

    def __init__(self, char_probs: TextStatistics):
        self.table = CharProbTable.from_twograms(char_probs.twograms)

    @classmethod
    def from_pickle(cls, path):
        import pickle
        char_probs = pickle.load(open(path, "rb"))
        return cls(char_probs)

    def generate_word(self, table, chars):
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
        try:
            table = self.table.retain(lambda c1, c2: (c1 in args.chars or c1 == " ") and c2 in args.chars)

            target_len = random.randrange(args.min_length, args.max_length)

            acc = ""
            while len(acc) < target_len:
                acc += self.generate_word(table, args.chars) + " "
            if len(acc) > args.max_length:
                acc = acc[:args.max_length]
            return acc.rstrip()
        except KeyError:
            raise CannotGenerateText(f"Unable to generate text with chars {args.chars!r}, available are {''.join(sorted(self.table.table.keys())).strip()!r}")
