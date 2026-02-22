from dataclasses import dataclass, field


@dataclass
class Hand:
    private: list = field(default_factory=list)
    revealed: list = field(default_factory=list)
    received: list = field(default_factory=list)


@dataclass
class PlayerState:
    model: object
    coins: int = 0
    loans: int = 0
    invests: int = 0
    hands: Hand = field(default_factory=Hand)


@dataclass
class Decks:
    auctions: object = None
    gems: object = None


@dataclass
class LastAuction:
    bids: list = field(default_factory=list)
    winner: object = None


@dataclass
class State:
    decks: Decks = field(default_factory=Decks)
    auction: object = None
    gems: list = field(default_factory=list)
    last_auction: LastAuction = field(default_factory=LastAuction)
    players: list[PlayerState] = field(default_factory=list)
