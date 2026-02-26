import random
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Models import ObservedGameState

random.seed(42)


class Player:
    def __init__(self, id: int):
        self.id = id

    def make_bid(self, state: "ObservedGameState") -> int:
        raise

    def make_reveal(self, state: "ObservedGameState") -> int:
        raise


class RandomPlayer(Player):
    def make_bid(self, state: "ObservedGameState") -> int:
        auction = state.auction
        max_bid = state.players[self.id].coins
        if auction == 2:
            max_bid += 10
        elif auction == 3:
            max_bid += 20

        bid = random.randint(0, max_bid)
        return bid

    def make_reveal(self, state: "ObservedGameState") -> int:
        return random.choice(state.players[self.id].to_reveal)


class SmartRandomPlayer(Player):
    def make_bid(self, state: "ObservedGameState") -> int:
        auction = state.auction
        max_bid = state.players[self.id].coins
        if auction == 2:
            max_bid += 10
        elif auction == 3:
            max_bid += 20

        max_bid = max_bid // 2
        bid = random.randint(0, max_bid)
        return bid

    def make_reveal(self, state: "ObservedGameState") -> int:
        return random.choice(state.players[self.id].to_reveal)
