from collections import defaultdict
import textprovider
from textprovider.statistical import TextStatistics


def collect_statistics(text, allowed_chars=None):
    allowed_chars = set(allowed_chars or textprovider.Charset.EVERYTHING)
    twograms = defaultdict(int)
    char_count = defaultdict(int)

    import re

    words = filter(lambda word: all(c in allowed_chars for c in word), re.split("\\s+", text.lower()))

    for word in words:
        word = " " + word + " "
        for c1, c2 in zip(word[:-1], word[1:]):
            char_count[c1] += 1
            twograms[c1 + c2] += 1


    return TextStatistics(twograms, char_count, allowed_chars)


if __name__ == "__main__":
    source_file = input("Input source file:")
    dump_file = input("Input dump file:") or "assets\\text_statistics\\stats_1.pickle"

    text = open(source_file, "r").read()
    stats = collect_statistics(text)

    import pickle
    pickle.dump(stats, open(dump_file, "w+b"))

    print(stats)
    print("Dumped successfully to", dump_file)