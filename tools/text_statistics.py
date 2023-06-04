from collections import defaultdict
import textprovider
from textprovider.statistical import TextStatistics


def collect_statistics(text, allowed_chars=None):
    """
    TODO
    :param text: geschriebener Text
    :param allowed_chars: in die Auswertung einbezogene Zeichen
    :return: TextStatistics-Objekt mit berechneten Werten
    """
    allowed_chars = set(allowed_chars or textprovider.Charset.EVERYTHING)
    twograms = defaultdict(int)
    char_count = defaultdict(int)

    import re

    words = re.split("\\s+", text)

    for word in words:
        if any(c not in allowed_chars for c in word):
            continue
        word = " " + word + " "
        for c1, c2 in zip(word[:-1], word[1:]):
            char_count[c1] += 1
            twograms[c1 + c2] += 1


    return TextStatistics(twograms, char_count, allowed_chars)


if __name__ == "__main__":
    source_file = input("Input source file:")
    dump_file = input("Input dump file:") or "assets\\text_statistics\\stats_1.pickle"
    lower_all = not input("All chars lowercase? [Enter=Yes]") and True
    print(repr(lower_all))

    text = open(source_file, "r", encoding="UTF-8").read()
    stats = collect_statistics(text.lower() if bool(lower_all) else text)

    import pickle
    pickle.dump(stats, open(dump_file, "w+b"))

    print(stats)
    print("Dumped successfully to", dump_file)