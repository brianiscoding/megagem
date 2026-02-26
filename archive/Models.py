from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Player import Player


@dataclass
class LastAuction:
    bids: list[int] = None
    winner_id: int = None
    reveal: int = None


@dataclass
class GameState:
    deck_auction = None
    deck_gem = None
    auction = None
    gems = None
    last_auction = None
    players = None
    winners = None


@dataclass
class PlayerState:
    model: "Player"
    coins: int = 0
    loans: int = 0
    invests: int = 0
    hand: list[int] = field(default_factory=list)
    hand_mask: list[bool] = field(default_factory=list)
    collection: list[int] = field(default_factory=list)


class ObservedPlayerState:
    def __init__(self, player: PlayerState, reveal_hand: bool = False):
        self._player = player
        self._reveal_hand = reveal_hand

    @property
    def coins(self):
        return self._player.coins

    @property
    def loans(self):
        return self._player.loans

    @property
    def invests(self):
        return self._player.invests

    @property
    def to_reveal(self):
        return [i for i, e in enumerate(self._player.hand_mask) if not e]

    @property
    def collection(self):
        return self._player.collection

    @property
    def hand(self):
        if self._reveal_hand:
            return self._player.hand
        return [self._player_hand[i] for i, e in enumerate(self._player.hand_mask) if e]


class ObservedGameState:
    def __init__(self, game, player_id: int):
        self._game = game
        self._player_id = player_id
        self._players = [
            ObservedPlayerState(p, reveal_hand=(i == self._player_id))
            for i, p in enumerate(self._game._players)
        ]

    @property
    def auction(self):
        return self._game._auction

    @property
    def gems(self):
        return self._game._gems

    @property
    def last_auction(self):
        return self._game._last_auction

    @property
    def players(self):
        return self._players
