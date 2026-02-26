import random
from Materials import SETUP


class Player:
    def __init__(self, num_players, player_id, hand):
        self.n = num_players
        self.pid = player_id

    def bid(self, state):
        return 0

    def reveal(self, bids):
        return 0


class RandomPlayer(Player):
    def __init__(self, num_players, player_id, hand):
        super().__init__(num_players, player_id, hand)

        self.hand = hand
        self.last_auction = None
        self.coins = SETUP[num_players][0]

    def bid(self, state):
        if state.last_auction.wid == self.pid:
            match self.last_auction:
                case 0 | 1 | 4 | 5:
                    self.coins -= state.last_auction.bids[self.pid]
                case 2:
                    self.coins += 10 - state.last_auction.bids[self.pid]
                case 3:
                    self.coins += 20 - state.last_auction.bids[self.pid]
                case None:
                    pass

        limit_bid = self.coins
        match state.auction:
            case 2:
                limit_bid += 10
            case 3:
                limit_bid += 20
        limit_bid = int(limit_bid * 0.6)
        bid = random.randint(0, limit_bid)

        self.last_auction = state.auction
        return bid
