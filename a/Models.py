from dataclasses import dataclass, field


@dataclass
class PlayerState:
    model: any = None
    coins: int = None
    loans: int = None
    invests: int = None
    hand: list[int] = None
    collection: list[int] = None
    score: int = None


@dataclass
class Log:
    bids: list[int] = None
    wid: int = None
    reveal: int = None


@dataclass
class Settings:
    freqs_auction: list[int] = None
    freqs_gem: list[int] = None
    value_chart: list[int] = None


@dataclass
class GameState:
    settings: Settings = None
    deck_auction: list[int] = None
    deck_gem: list[int] = None
    auction: int = None
    gems: list[int] = None
    players: list[PlayerState] = None
    logs: list[str] = None
    winners = None


@dataclass
class Node:
    game: any = None
    parent: "Node" = None
    visits: int = 0
    wins: int = 0
    children: list[list["Node"]] = None
