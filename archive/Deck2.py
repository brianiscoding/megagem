from math import ceil, log2
import random

random.seed(42)


class Deck:
    def __init__(self, template):
        self.e_size = None
        self.n_size = None
        self.i = None
        self.n = None
        self.encode(template)

    def encode(self, template):
        self.e_size = ceil(log2(max(template) + 1))

        expanded = [i for i, count in enumerate(template) for _ in range(count)]
        # random.shuffle(expanded)

        s = "".join(f"{v:0{self.e_size}b}" for v in expanded)
        self.n_size = len(s)
        self.i = self.n_size
        self.n = int(s, 2)

    def pop(self):
        self.i -= self.e_size
        return (self.n >> self.i) & ((1 << self.e_size) - 1)

    def __len__(self):
        return self.i // self.e_size
