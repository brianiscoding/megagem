import random

random.seed(42)


class Deck:
    def __init__(self, template):
        self.cards = [i for i, count in enumerate(template) for _ in range(count)]
        random.shuffle(self.cards)

    def pop(self):
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return self.cards.__repr__()
