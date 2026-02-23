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


@dataclass
class ObservedPlayerState:
    coins: int = 0
    loans: int = 0
    invests: int = 0
    hand: list[int] = field(default_factory=list)
    to_reveal: list[int] = field(default_factory=list)
    collection: list[int] = field(default_factory=list)


@dataclass
class ObservedGameState:
    auction: int
    gems: list[int]
    last_auction: LastAuction
    players: list[PlayerState]
