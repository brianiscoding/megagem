import random

random.seed(42)


class Player:
    def __init__(self, id: int):
        self.id = id

    def make_bid(self, state: dict) -> int:
        coins = state["players"][self.id]["coins"]
        auction = state["auction"]
        max_bid = coins
        if auction == 2:
            max_bid += 10
        elif auction == 3:
            max_bid += 20
        bid = random.randint(0, max_bid)

        return bid

    def make_reveal(self, state: dict) -> int:
        """Override to implement reveal logic."""

        return 0  # Placeholder implementation
