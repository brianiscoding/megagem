import random
from Materials import GEMS, SETUP, AUCTIONS
import bisect
from Deck import Deck
from Models import LastAuction, PlayerState, ObservedGameState
from Player import Player


class Game:
    def __init__(self, players: list[Player]):
        self._round = 0
        self._deck_auction: Deck = None
        self._deck_gem: Deck = None
        self._auction: int = None
        self._gems: list[int] = []
        self._last_auction: LastAuction = LastAuction()
        self._players: list[Player] = [
            PlayerState(model=players[i](i)) for i in range(len(players))
        ]

        self.logs = [None]
        self._run()

    def _run(self) -> None:
        self._setup()
        while not self._is_over():
            self._update()
        self._teardown()

    def _setup(self) -> None:
        lp = len(self._players)
        self._deck_auction = Deck(template=AUCTIONS)
        self._deck_gem = Deck(template=GEMS)

        for i in range(lp):
            self._players[i].coins = SETUP[lp][0]
            self._players[i].hand = [self._deck_gem.pop() for _ in range(SETUP[lp][1])]
            self._players[i].hand_mask = [False for _ in range(SETUP[lp][1])]

        self._auction = self._deck_auction.pop()
        for _ in range(2):
            self._draw_gem()

    def _update(self) -> None:
        self._phase_bid()
        self._reveal_phase()

        winner = self._last_auction.winner_id
        bids = self._last_auction.bids
        reveal = self._last_auction.reveal
        self.logs.append((bids, winner, reveal))

    def _phase_bid(self) -> None:
        bids = []
        auction = self._auction

        for i, player in enumerate(self._players):
            state = ObservedGameState(game=self, player_id=i)
            bid = player.model.make_bid(state)
            allowed_max = player.coins + (
                10 if auction == 2 else 20 if auction == 3 else 0
            )
            if not (0 <= bid <= allowed_max):
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
        elif self._last_auction.winner_id != None:
            winner_id = winner_ids[
                (bisect.bisect_left(winner_ids, self._last_auction.winner_id) - 1)
                % len(winner_ids)
            ]
        else:
            winner_id = random.choice(winner_ids)

        match self._auction:
            case 0:
                self._players[winner_id].coins -= max_bid
                self._receive_gem(winner_id)
            case 1:
                self._players[winner_id].coins -= max_bid
                self._receive_gem(winner_id)
                self._receive_gem(winner_id)
            case 2:
                self._players[winner_id].loans += 10
                self._players[winner_id].coins += 10 - max_bid
            case 3:
                self._players[winner_id].loans += 20
                self._players[winner_id].coins += 20 - max_bid
            case 4:
                self._players[winner_id].coins -= max_bid
                self._players[winner_id].invests += max_bid + 5
            case 5:
                self._players[winner_id].coins -= max_bid
                self._players[winner_id].invests += max_bid + 10

        self._last_auction.bids = bids
        self._last_auction.winner_id = winner_id

    def _reveal_phase(self) -> None:
        winner_id = self._last_auction.winner_id
        if not all(self._players[winner_id].hand_mask):
            player = self._players[winner_id].model
            state = ObservedGameState(game=self, player_id=winner_id)
            reveal_i = player.make_reveal(state)
            if (
                not 0 <= reveal_i <= SETUP[len(self._players)][1]
                or self._players[winner_id].hand_mask[reveal_i]
            ):
                raise
            self._players[winner_id].hand_mask[reveal_i] = True
            self._last_auction.reveal = self._players[winner_id].hand[reveal_i]
        else:
            self._last_auction.reveal = None

        match self._auction:
            case 0:
                self._draw_gem()
            case 1:
                self._draw_gem()
                self._draw_gem()

        self._auction = self._deck_auction.pop()
        self._round += 1

    def _is_over(self) -> bool:
        if self._round >= 100:
            return exit(1)
        if len(self._gems) == 0 and len(self._deck_gem) == 0:
            return True

    def _teardown(self) -> None:
        pass

    def _draw_gem(self) -> None:
        try:
            self._gems.insert(0, self._deck_gem.pop())
        except:
            pass

    def _receive_gem(self, i) -> None:
        try:
            gem = self._gems.pop()
            self._players[i].collection.append(gem)
        except:
            pass
