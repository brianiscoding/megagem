from typing import Any
import random
from Materials import GEMS, SETUP, AUCTIONS
from Player import Player
import bisect
from Deck import Deck


class Game:
    def __init__(self, players: list[Any]):
        self.logs = [None]
        self.round = 0
        self.state = {
            "decks": {
                "auctions": None,
                "gems": None,
            },
            "auction": None,
            "gems": [],
            "last_auction": {
                "bids": [],
                "winner": None,
            },
            "players": [
                {
                    "model": players[i](i),
                    "coins": 0,
                    "loans": 0,
                    "invests": 0,
                    "hands": {
                        "private": [],
                        "revealed": [],
                        "received": [],
                    },
                }
                for i in range(len(players))
            ],
        }
        self.results = None

        self.run()

    def run(self) -> dict:
        self.setup()
        while not self.is_over():
            self.update()
        self.teardown()

    def setup(self) -> None:
        lp = len(self.state["players"])
        self.state["decks"]["auctions"] = Deck(template=AUCTIONS)
        self.state["decks"]["gems"] = Deck(template=GEMS)

        for i in range(lp):
            self.state["players"][i]["coins"] = SETUP[lp][0]
            self.state["players"][i]["hands"]["private"] = [
                self.state["decks"]["gems"].pop() for _ in range(SETUP[lp][1])
            ]

        self.state["auction"] = self.state["decks"]["auctions"].pop()
        self.state["gems"] = [self.state["decks"]["gems"].pop() for _ in range(2)]

    def update(self) -> None:
        bids = self._get_bids()
        winner = self._resolve_bids(bids)
        reveal = self._get_reveal(winner)
        self.end_round(winner, reveal)

        self.logs.append((bids, winner, reveal))

    def _get_bids(self) -> int:
        bids = []
        auction = self.state["auction"]

        for i, player in enumerate(self.state["players"]):
            state = self.get_state(i)
            bid = player["model"].make_bid(state)
            max_bid = player["coins"] + (
                10 if auction == 2 else 20 if auction == 3 else 0
            )
            if bid < 0 or bid > max_bid:
                raise ValueError(f"Player {i} made an invalid bid: {bid}")
            bids.append(bid)
        return bids

    def _resolve_bids(self, bids: list[int]) -> int:
        max_bid = float("-inf")
        winners = []
        for i, bid in enumerate(bids):
            if bid > max_bid:
                max_bid = bid
                winners = [i]
            elif bid == max_bid:
                winners.append(i)

        if len(winners) == 1:
            winner = winners[0]
        elif self.state["last_auction"]["winner"] == None:
            winner = random.choice(winners)
        else:
            winner = winners[
                (bisect.bisect_left(winners, self.state["last_auction"]["winner"]) - 1)
                % len(winners)
            ]

        self.state["players"][winner]["coins"] -= max_bid
        match self.state["auction"]:
            case 0:
                self._receive_gem(winner)
            case 1:
                self._receive_gem(winner)
                if len(self.state["gems"]) != 0:
                    self._receive_gem(winner)
            case 2:
                self.state["players"][winner]["loans"] += 10
                self.state["players"][winner]["coins"] += 10
            case 3:
                self.state["players"][winner]["loans"] += 20
                self.state["players"][winner]["coins"] += 20
            case 4:
                self.state["players"][winner]["invests"] += max_bid + 5
            case 5:
                self.state["players"][winner]["invests"] += max_bid + 10

        # print(self.round + 1, bids, winner)

        self.state["last_auction"] = {"bids": bids, "winner": winner}
        return winner

    def _receive_gem(self, i):
        self.state["players"][i]["hands"]["received"].append(self.state["gems"].pop())

    def _get_reveal(self, i) -> int:
        if len(self.state["players"][i]["hands"]["private"]) == 0:
            return None
        player = self.state["players"][i]["model"]
        state = self.get_state(i)
        reveal = player.make_reveal(state)
        if reveal < 0 or reveal >= len(self.state["players"][i]["hands"]["private"]):
            raise ValueError(f"Player {i} made an invalid reveal: {reveal}")
        return reveal

    def end_round(self, winner, reveal) -> None:
        if reveal is not None:
            gem = self.state["players"][winner]["hands"]["private"].pop(reveal)
            self.state["players"][winner]["hands"]["revealed"].append(gem)

        match self.state["auction"]:
            case 0:
                self._draw_gem()
            case 1:
                self._draw_gem()
                self._draw_gem()

        self.state["auction"] = self.state["decks"]["auctions"].pop()
        self.round += 1

    def _draw_gem(self):
        if len(self.state["decks"]["gems"]) <= 0:
            return
        self.state["gems"].insert(0, self.state["decks"]["gems"].pop())

    def render(self):
        log = self.logs[-1]
        s = self.state

        bids = str(log[0]) if log else ""
        winner = log[1] if log and log[1] is not None else ""
        reveal = log[2] if log and log[2] is not None else ""
        gems = s["gems"]
        auction = s["auction"]
        gd = len(s["decks"]["gems"])
        ad = len(s["decks"]["auctions"])
        players = s["players"]

        players_str = ""

        for p in players:
            players_str += f"{p['model'].id}: cs={p['coins']:<2} lo={p['loans']:<2} in={p['invests']:<2} "
            players_str += f"pri={p['hands']['private'].__repr__():<12} "
            players_str += f"rev={p['hands']['revealed'].__repr__():<12} "
            players_str += f"rec={p['hands']['received']}\n"

        line = (
            f"{players_str}"
            f"R{self.round} bids={bids:<16} win={winner:<1} rev={reveal:<1} gems={gems.__repr__():<6} auc={auction:<1} gd={gd:>2} ad={ad:>2}\n"
        )

        with open("log.txt", "a") as f:
            f.write(line + "\n")

    def is_over(self) -> bool:
        """Return True when the game loop should stop."""
        if self.round >= 100:
            return True
        if len(self.state["gems"]) == 0 and len(self.state["decks"]["gems"]) == 0:
            return True

    def get_state(self, i: int) -> dict:
        return self.state

    def teardown(self) -> dict:
        """Return any final results after the game ends. Override to customize."""
        return {"rounds": self.round}


import time


def benchmark(seconds):
    count = 0
    end = time.time() + seconds
    while time.time() < end:
        Game(players=[Player, Player, Player, Player])
        count += 1
    print(f"{count} calls in {seconds} seconds ({count/seconds:.0f}/sec)")


if __name__ == "__main__":
    Game(players=[Player, Player, Player, Player])
    benchmark(20)
