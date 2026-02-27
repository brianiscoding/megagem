from Players import Player, RandomPlayer
from ISMCTS import ISMCTS_Player
import time

from Materials import FREQS_GEM, FREQS_AUCTION, VALUE_CHART
from Game import init_game, rollout

models = [ISMCTS_Player, Player, Player, Player]
models = [ISMCTS_Player, RandomPlayer, RandomPlayer, RandomPlayer]


def benchmark(seconds):
    count = 0
    end = time.time() + seconds

    winner_freqs = [0 for _ in range(4)]
    while time.time() < end:
        g = init_game(FREQS_AUCTION, FREQS_GEM, VALUE_CHART, models)
        rollout(g)
        for id in g.winners:
            winner_freqs[id] += 1
        count += 1
    print([round(e / count, 2) for e in winner_freqs])
    print(f"{count} calls in {seconds} seconds ({count/seconds:.0f}/sec)")


def main():
    x = True
    x = False
    if x:
        g = init_game(FREQS_AUCTION, FREQS_GEM, VALUE_CHART, models)
        rollout(g)
        print(g.winners)
    else:
        benchmark(100)


if __name__ == "__main__":
    main()
