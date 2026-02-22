import random

random.seed(42)


class Deck:
    def __init__(self, template):
        self.cards = []
        for i, count in enumerate(template):
            self.cards.extend([i] * count)

    def shuffle(self):
        random.shuffle(self.cards)

    def pop(self):
        if not self.cards:
            raise IndexError("Deck is empty")
        return self.cards.pop()

    def __len__(self):
        return len(self.cards)

    def __repr__(self):
        return self.cards.__repr__()
