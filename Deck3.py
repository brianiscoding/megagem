import random

random.seed(42)


class Deck:
    def __init__(self, template):
        self.cards = []
        self.i = 0
        for i, count in enumerate(template):
            self.cards.extend([i] * count)
        random.shuffle(self.cards)

    def pop(self):
        self.i += 1
        return self.cards[self.i - 1]

        if not self.cards:
            raise IndexError("Deck is empty")
        return self.cards.pop()

    def __len__(self):
        return len(self.cards) - self.i

    def __repr__(self):
        return self.cards.__repr__()
