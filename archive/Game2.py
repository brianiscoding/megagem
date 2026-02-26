import random
from Materials import GEMS, SETUP, AUCTIONS, VALUE_CHART
import bisect
from Deck import Deck
from Models import LastAuction, PlayerState, ObservedGameState, GameState
from Player import Player
from dataclasses import dataclass, field


def create_deck(template):
    deck = [i for i, count in enumerate(template) for _ in range(count)]
    random.shuffle(deck)
    return deck


@dataclass
class LastAuction:
    bids: list[int] = None
    winner_id: int = None
    reveal: int = None


@dataclass
class PlayerState:
    coins: int = None
    loans: int = 0
    invests: int = 0
    hand: list[int] = None
    hand_mask: list[bool] = None
    collection: list[int] = None


@dataclass
class GameState:
    deck_auction: list[int] = None
    deck_gem: list[int] = None
    last_auction: LastAuction = field(default_factory=LastAuction)
    players: list[PlayerState] = None
    winners = None


class Game:
    def __init__(self, size=None, state=None):
        self.state = None

        if size:
            self.state = GameState(
                deck_auction=create_deck(AUCTIONS),
                deck_gem=create_deck(GEMS),
                players=[PlayerState() for _ in range(size)],
            )
            for pid in range(size):
                self.state.players[pid].coins = SETUP[size][0]
                self.state.players[pid].hand = [
                    self.state.deck_gem.pop() for _ in range(SETUP[size][1])
                ]
                self.state.players[pid].hand_mask = [
                    False for _ in range(SETUP[size][1])
                ]
                self.state.players[pid].collection = [0 for _ in range(len(GEMS))]

        if state:
            self.state = state

    def play(self, bids):
        auction = self.state.deck_auction[-1]
        max_bid = float("-inf")
        wids = []
        for i, bid in enumerate(bids):
            limit_bid = self.state.players[i].coins + (
                10 if auction == 2 else 20 if auction == 3 else 0
            )
            if not (0 <= bid <= limit_bid):
                raise
            if bid > max_bid:
                max_bid = bid
                wids = [i]
            elif bid == max_bid:
                wids.append(i)

        if len(wids) == 1:
            wid = wids[0]
        elif self.state.last_auction.winner_id != None:
            wid = wids[
                (bisect.bisect_left(wids, self.state.last_auction.winner_id) - 1)
                % len(wids)
            ]
        else:
            wid = random.choice(wids)

        match auction:
            case 0:
                self.state.players[wid].coins -= max_bid
                self._collect_gem(wid)
            case 1:
                self.state.players[wid].coins -= max_bid
                self._collect_gem(wid)
                self._collect_gem(wid)
            case 2:
                self.state.players[wid].loans += 10
                self.state.players[wid].coins += 10 - max_bid
            case 3:
                self.state.players[wid].loans += 20
                self.state.players[wid].coins += 20 - max_bid
            case 4:
                self.state.players[wid].coins -= max_bid
                self.state.players[wid].invests += max_bid + 5
            case 5:
                self.state.players[wid].coins -= max_bid
                self.state.players[wid].invests += max_bid + 10

        if len(self.state.deck_gem) == 0:
            self.state.winners = [67]
            return

        self.state.last_auction.bids = bids
        self.state.last_auction.winner_id = wid

        if not all(self.state.players[wid].hand_mask):
            reveal_id = random.choice(
                [i for i, e in enumerate(self.state.players[wid].hand_mask) if not e]
            )
            self.state.players[wid].hand_mask[reveal_id] = True
            card = self.state.players[wid].hand[reveal_id]
            self.state.last_auction.reveal = card
        else:
            self.state.last_auction.reveal = None

        self.state.deck_auction.pop()

    def _collect_gem(self, pid):
        try:
            card = self.state.deck_gem.pop()
            self.state.players[pid].collection[card] += 1
        except:
            pass


def main():
    game = Game(size=4)
    print(game.state)
    while True:
        # input("+++")
        bids = random_bids(game.state)
        game.play(bids)
        print(game.state)
        if game.state.winners:
            break
    print(game.state.winners)


def random_bids(state):
    auction = state.deck_auction[-1]
    bids = []
    for player in state.players:
        limit_bid = player.coins + (10 if auction == 2 else 20 if auction == 3 else 0)
        bids.append(random.randint(0, limit_bid))
    return bids


if __name__ == "__main__":
    main()

freqs = []
