from Players import Player, RandomPlayer
from Models import Node
import copy
import random
from Game import play, rollout
import math


MIN_SAMPLES = 10
N_LOOPS = 10 * MIN_SAMPLES
EXPLORATION = 1.41


class ISMCTS_Player(Player):
    def bid(self, limit_bid):
        root = self.create_root(self.game, limit_bid)
        for _ in range(N_LOOPS):
            node = self.select(root)
            if node.game.winners is None:
                node = self.expand(node)
                result = self.simulate(node)
            else:
                result = 1 if self.pid in node.game.winners else 0
            self.backpropagate(node, result)
        best_bid = self.best_action(root)
        return best_bid

    def select(self, node):
        while (
            sum(len(row) for row in node.children) >= MIN_SAMPLES
            and node.game.winners is None
        ):
            node = self.best_child(node)
        return node

    def best_child(self, node):
        def ucb1(row):
            total_visits = sum(c.visits for c in row)
            total_wins = sum(c.wins for c in row)
            if total_visits == 0:
                return float("inf")
            return (total_wins / total_visits) + EXPLORATION * math.sqrt(
                math.log(node.visits) / total_visits
            )

        best_row = max((row for row in node.children if row), key=lambda row: ucb1(row))
        return random.choice(best_row)

    def backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    def best_action(self, root):
        best_bid, _ = max(
            (
                (bid, sum(c.visits for c in row))
                for bid, row in enumerate(root.children)
            ),
            key=lambda x: x[1],
        )
        return best_bid

    def expand(self, node):
        if node.game.winners:
            return node
        child = self.create_child(node)
        action = child.game.logs[-1].bids[self.pid]
        node.children[action].append(child)
        return child

    def simulate(self, node):
        copied = copy.deepcopy(node.game)
        rollout(copied)
        return 1 if self.pid in copied.winners else 0

    def create_root(self, game, limit_bid):
        copied = copy.deepcopy(game)
        random.shuffle(copied.deck_auction)
        random.shuffle(copied.deck_gem)
        return Node(game=copied, children=[[] for _ in range(limit_bid + 1)])

    def create_child(self, node):
        copied = copy.deepcopy(node.game)
        random.shuffle(copied.deck_auction)
        random.shuffle(copied.deck_gem)
        for pid in range(len(node.game.players)):
            copied.players[pid].model = RandomPlayer(copied, pid)
        play(copied)
        n_children = (
            copied.players[self.pid].coins
            + (10 if copied.auction == 2 else 20 if copied.auction == 3 else 0)
            + 1
        )
        return Node(game=copied, parent=node, children=[[] for _ in range(n_children)])
