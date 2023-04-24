import random

from textprovider import TextProvider, TextProviderArgs, random_word_len


class RandomTextProvider(TextProvider):
    def __init__(self, wordlen):
        self.wordlen = wordlen

    def get_word(self, length, chars):
        return "".join(random.choice(chars) for _ in range(length))

    def get_text(self, args: TextProviderArgs):
        target_length = random.randrange(args.min_length, args.max_length)
        acc = ""
        while len(acc) < target_length:
            wordlen = random_word_len()
            acc += self.get_word(wordlen, args.chars) + " "
        if len(acc) > args.max_length:
            acc = acc[:args.max_length]
        return acc.rstrip()



