import time
from Game import Game
from Player import Player


def benchmark(seconds):
    count = 0
    end = time.time() + seconds
    while time.time() < end:
        Game(players=[Player, Player, Player, Player])
        count += 1
    print(f"{count} calls in {seconds} seconds ({count/seconds:.0f}/sec)")


if __name__ == "__main__":
    Game(players=[Player, Player, Player, Player])
    benchmark(20)
