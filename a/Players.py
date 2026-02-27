import random


class Player:
    def __init__(self, game_state, player_id):
        self.game = game_state
        self.pid = player_id

    def bid(self, limit_bid):
        return 0

    def reveal(self, hand, bids):
        return hand[0]


class RandomPlayer(Player):
    def bid(self, limit_bid):
        return random.randint(0, limit_bid)
