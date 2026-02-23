import random
from Materials import GEMS, SETUP, AUCTIONS
import bisect
from Deck import Deck
from Models import LastAuction, PlayerState, ObservedGameState, ObservedPlayerState
from Player import Player


class Game:
    def __init__(self, players: list[Player]):
        self.round = 0
        self.deck_auction: Deck = None
        self.deck_gem: Deck = None
        self.auction: int = None
        self.gems: list[int] = None
        self.last_auction: LastAuction = None
        self.players: list[Player] = [
            PlayerState(model=players[i](i)) for i in range(len(players))
        ]

        self.logs = [None]
        self.run()

    def run(self) -> dict:
        self.setup()
        # self.render()
        while not self.is_over():
            self.update()
            # self.render()

        self.teardown()

    def setup(self) -> None:
        # with open("log.txt", "w") as f:
        #     pass

        lp = len(self.players)
        self.deck_auction = Deck(template=AUCTIONS)
        self.deck_gem = Deck(template=GEMS)

        for i in range(lp):
            self.players[i].coins = SETUP[lp][0]
            self.players[i].hand = [self.deck_gem.pop() for _ in range(SETUP[lp][1])]
            self.players[i].hand_mask = [False for _ in range(SETUP[lp][1])]

        self.auction = self.deck_auction.pop()
        self.gems = [self.deck_gem.pop() for _ in range(2)]

    def update(self) -> None:
        self._phase_bid()
        self._reveal_phase()

        winner = self.last_auction.winner_id
        bids = self.last_auction.bids
        reveal = self.last_auction.reveal
        self.logs.append((bids, winner, reveal))

    def _phase_bid(self) -> int:
        bids = []
        auction = self.auction

        for i, player in enumerate(self.players):
            state = self.get_observed_game_state(i)
            bid = player.model.make_bid(state)
            max_bid = player.coins + (10 if auction == 2 else 20 if auction == 3 else 0)
            if bid < 0 or bid > max_bid:
                raise
            bids.append(bid)

        max_bid = float("-inf")
        winner_ids = []
        for i, bid in enumerate(bids):
            if bid > max_bid:
                max_bid = bid
                winner_ids = [i]
            elif bid == max_bid:
                winner_ids.append(i)

        if len(winner_ids) == 1:
            winner_id = winner_ids[0]
        elif self.last_auction != None:
            winner_id = winner_ids[
                (bisect.bisect_left(winner_ids, self.last_auction.winner_id) - 1)
                % len(winner_ids)
            ]
        else:
            winner_id = random.choice(winner_ids)

        match self.auction:
            case 0:
                self.players[winner_id].coins -= max_bid
                self._receive_gem(winner_id)
            case 1:
                self.players[winner_id].coins -= max_bid
                self._receive_gem(winner_id)
                self._receive_gem(winner_id)
            case 2:
                self.players[winner_id].loans += 10
                self.players[winner_id].coins += 10 - max_bid
            case 3:
                self.players[winner_id].loans += 20
                self.players[winner_id].coins += 20 - max_bid
            case 4:
                self.players[winner_id].coins -= max_bid
                self.players[winner_id].invests += max_bid + 5
            case 5:
                self.players[winner_id].coins -= max_bid
                self.players[winner_id].invests += max_bid + 10

        self.last_auction = LastAuction(bids=bids, winner_id=winner_id)

    def _receive_gem(self, i):
        try:
            gem = self.gems.pop()
            self.players[i].collection.append(gem)
        except:
            pass

    def _reveal_phase(self) -> int:
        winner_id = self.last_auction.winner_id
        if not all(self.players[winner_id].hand_mask):
            player = self.players[winner_id].model
            state = self.get_observed_game_state(winner_id)
            reveal_i = player.make_reveal(state)
            if (
                not 0 <= reveal_i <= SETUP[len(self.players)][1]
                or self.players[winner_id].hand_mask[reveal_i]
            ):
                raise
            self.players[winner_id].hand_mask[reveal_i] = True
            self.last_auction.reveal = self.players[winner_id].hand[reveal_i]
        else:
            self.last_auction.reveal = None

        match self.auction:
            case 0:
                self._draw_gem()
            case 1:
                self._draw_gem()
                self._draw_gem()

        self.auction = self.deck_auction.pop()
        self.round += 1

    def _draw_gem(self):
        try:
            self.gems.insert(0, self.deck_gem.pop())
        except:
            pass

    def render(self):
        log = self.logs[-1]

        bids = str(log[0]) if log else ""
        winner = log[1] if log and log[1] is not None else ""
        reveal = log[2] if log and log[2] is not None else ""
        gems = self.gems
        auction = self.auction
        gd = len(self.deck_gem)
        ad = len(self.deck_auction)
        players = self.players

        players_str = ""

        for p in players:
            players_str += (
                f"{p.model.id}: cs={p.coins:<2} lo={p.loans:<2} in={p.invests:<2} "
            )
            players_str += f"hand={p.hand.__repr__():<12} "
            players_str += f"pub={"".join("1" if x else "0" for x in p.hand_mask) } "
            players_str += f"col={p.collection}\n"

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
        if len(self.gems) == 0 and len(self.deck_gem) == 0:
            return True

    def get_observed_game_state(self, player_id: int) -> dict:
        players = []
        for curr_player_id, player in enumerate(self.players):
            if curr_player_id == player_id:
                players.append(
                    ObservedPlayerState(
                        coins=player.coins,
                        loans=player.coins,
                        invests=player.invests,
                        hand=player.hand,
                        to_reveal=[i for i, e in enumerate(player.hand_mask) if not e],
                        collection=player.collection,
                    )
                )
                continue

            hand, to_reveal = [], []
            for i, e in enumerate(player.hand_mask):
                if e:
                    hand.append(player.hand[i])
                else:
                    to_reveal.append(i)
            players.append(
                ObservedPlayerState(
                    coins=player.coins,
                    loans=player.coins,
                    invests=player.invests,
                    hand=hand,
                    to_reveal=to_reveal,
                    collection=player.collection,
                )
            )

        return ObservedGameState(
            auction=self.auction,
            gems=self.gems,
            players=players,
            last_auction=self.last_auction,
        )

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
