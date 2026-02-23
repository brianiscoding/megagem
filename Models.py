from dataclasses import dataclass, field
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from Player import Player


@dataclass
class LastAuction:
    bids: list[int] = field(default_factory=list)
    winner_id: int = None
    reveal: int = None


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
        return [
            gem for gem, mask in zip(self._player.hand, self._player.hand_mask) if mask
        ]


@dataclass
class ObservedGameState:
    auction: int
    gems: list[int]
    last_auction: LastAuction
    players: list[PlayerState]
