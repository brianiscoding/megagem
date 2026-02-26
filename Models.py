from dataclasses import dataclass


@dataclass
class PlayerState:
    model: any = None
    coins: int = None
    loans: int = 0
    invests: int = 0
    hand: list[int] = None
    collection: list[int] = None


@dataclass
class LastAuction:
    bids: list[int] = None
    wid: int = None
    reveal: int = None


@dataclass
class ObservedState:
    auction: int = None
    gems: list[int] = None
    last_auction: LastAuction = None
