import random

random.seed(42)

import time

from Materials import AUCTIONS, GEMS

from Players import Player, RandomPlayer
from Game import Game
from ISMCTS import ISMCTS


# players = [Player, Player, Player, Player]
players = [ISMCTS, Player, Player, Player]


def benchmark(seconds):
    count = 0
    end = time.time() + seconds

    winner_freqs = [0 for _ in range(4)]
    while time.time() < end:
        game = Game()
        game.init(
            deck_auction_template=AUCTIONS, deck_gem_template=GEMS, players=players
        )
        game.rollout()
        for id in game.winners:
            winner_freqs[id] += 1
        count += 1
    print([round(e / count, 2) for e in winner_freqs])
    print(f"{count} calls in {seconds} seconds ({count/seconds:.0f}/sec)")


def pprint_players(ps):
    for p in ps:
        print(p.coins, p.loans, p.invests, p.collection)
    print("+++++")


if __name__ == "__main__":
    game = Game()
    game.init(deck_auction_template=AUCTIONS, deck_gem_template=GEMS, players=players)
    while not game.winners:
        game.play()
        # pprint_players(game.players)
    game.rollout()
    # pprint_players(game.players)

    print(game.winners)

    # benchmark(5)
    pass
