import time
from Game import Game
from Player import Player, RandomPlayer, SmartRandomPlayer


players = [SmartRandomPlayer, RandomPlayer, RandomPlayer, RandomPlayer]


def benchmark(seconds):
    count = 0
    end = time.time() + seconds

    winner_freqs = [0 for _ in range(4)]
    while time.time() < end:
        game = Game(players=players)
        for id in game.winners:
            winner_freqs[id] += 1
        count += 1
    print([round(e / count, 2) for e in winner_freqs])
    print(f"{count} calls in {seconds} seconds ({count/seconds:.0f}/sec)")


if __name__ == "__main__":
    # game = Game(players=players)
    # print(game.winners)

    benchmark(5)
    pass
