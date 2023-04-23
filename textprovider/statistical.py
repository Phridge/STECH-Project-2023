import dataclasses
from typing import Dict, Set

from . import TextProvider, TextProviderArgs

import random




@dataclasses.dataclass
class TextStatistics:
    twograms: Dict[str, int]
    char_count: Dict[str, int]
    allowed_chars: Set[str]


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
        followup_table = {}
        all_chars = set(pair[0] for pair, _ in char_probs.twograms.items())

        for char in all_chars:
            followup_chars = [(pair[1], count) for pair, count in char_probs.twograms.items() if pair[0] == char]
            total_count = sum(count for _, count in followup_chars)
            followup_chars = [(char, count / total_count) for char, count in followup_chars]
            followup_table[char] = followup_chars

        self.followup_table = followup_table



    @classmethod
    def from_pickle(cls, path):
        import pickle
        char_probs = pickle.load(open(path, "rb"))
        return cls(char_probs)

    def generate_word(self):
        current = " "
        acc = ""

        while True:
            next_options = self.followup_table[current]
            next_index = select_random(map(lambda x: x[1], next_options))
            next_char = next_options[next_index][0]
            if next_char == " ":
                break
            acc += next_char
            current = next_char

        return acc


    def get_reduced_followup_table(self, chars):
        pass

    def get_text(self, args: TextProviderArgs):
        acc = ""
        while True:
            acc += self.generate_word() + " "
            cutoff_chance = max(0., min(1., (len(acc) - args.min_length) / (args.max_length - args.min_length))) ** 2
            if random.random() < cutoff_chance:
                break
        if len(acc) > args.max_length:
            acc = acc[:args.max_length]
        return acc.rstrip()

