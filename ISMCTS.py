from Players import Player, RandomPlayer
from Game import Game
from dataclasses import dataclass
from Materials import GEMS, SETUP, AUCTIONS, VALUE_CHART
from Models import LastAuction, PlayerState

import math
import random


@dataclass
class MinimumPlayerState:
    coins: int = None
    loans: int = 0
    invests: int = 0
    collection: list[int] = None


class ISMCTS_Game(Game):
    def init(self, players, deck_auction, deck_gem, last_auction):
        self.deck_auction = deck_auction
        self.deck_gem = deck_gem
        self.last_auction = last_auction
        self.players = players

        print(players, deck_auction, deck_gem, last_auction)

    def copy(self):
        g = ISMCTS_Game()
        deck_auction = self.deck_auction[:]
        deck_gem = self.deck_gem[:]
        last_auction = LastAuction(
            bids=(
                self.last_auction.bids[:]
                if self.last_auction.bids is not None
                else None
            ),
            wid=self.last_auction.wid,
            reveal=self.last_auction.reveal,
        )
        players = [
            PlayerState(
                model=p.model,
                coins=p.coins,
                loans=p.loans,
                invests=p.invests,
                collection=p.collection[:],
            )
            for p in self.players
        ]
        g.init(players, deck_auction, deck_gem, last_auction)
        return g

    def shuffle(self):
        shuffled = self.deck_auction[:-1]
        random.shuffle(shuffled)
        self.deck_auction[:-1] = shuffled

        shuffled = self.deck_gem[:-2]
        random.shuffle(shuffled)
        self.deck_gem[:-2] = shuffled


class Node:
    def __init__(self):
        self.min_samples = 10

        self.game = None
        self.pid = None

        self.parent = None
        self.visits = None
        self.wins = None
        self.children = None

    def init_from_expand(self, parent):
        self.pid = parent.pid
        self.game = parent.game.copy()
        self.game.shuffle()
        self.visits = 0
        self.wins = 0

        auction = self.game.deck_auction[-1]
        limit_bid = self.game.players[self.pid].coins + (
            10 if auction == 2 else 20 if auction == 3 else 0
        )
        self.children = [[] for _ in range(limit_bid + 1)]

    def init_from_player(self, player, state):
        self.pid = player.pid

        self.game = ISMCTS_Game()
        deck_auction = [
            i for i, count in enumerate(player.freqs_auction) for _ in range(count)
        ]
        random.shuffle(deck_auction)
        deck_auction.append(state.auction)

        deck_gem = [i for i, count in enumerate(player.freqs_gem) for _ in range(count)]
        random.shuffle(deck_gem)
        deck_gem += state.gems

        n = len(player.players)
        players = [
            PlayerState(
                model=RandomPlayer(n, i), coins=p.coins, collection=p.collection
            )
            for i, p in enumerate(player.players)
        ]
        self.game.init(players, deck_auction, deck_gem, state.last_auction)

        self.visits = 0
        self.wins = 0

        limit_bid = player.players[player.pid].coins + (
            10 if state.auction == 2 else 20 if state.auction == 3 else 0
        )
        self.children = [[] for _ in range(limit_bid + 1)]

    def ended(self):
        return self.game.ended()

    def fully_expanded(self):
        return sum(len(row) for row in self.children) >= self.min_samples

    def untried(self):
        return [
            (bid, card_idx)
            for bid, row in enumerate(self.children)
            for card_idx, c in enumerate(row)
            if c is None
        ]

    def ucb1(self, exploration=1.41):
        if self.visits == 0:
            return float("inf")
        return (self.wins / self.visits) + exploration * math.sqrt(
            math.log(self.parent.visits) / self.visits
        )

    def best_child(self, exploration=1.41):
        return max(
            (c for row in self.children for c in row), key=lambda c: c.ucb1(exploration)
        )

    def __repr__(self):
        return (
            f"Node(visits={self.visits}, wins={self.wins}, "
            f"win_rate={self.wins/self.visits:.2f})"
            if self.visits > 0
            else "Node(unvisited)"
        )


class ISMCTS(Player):
    def __init__(self, num_players, player_id, hand):
        super().__init__(num_players, player_id, hand)
        self.exploration = 1.41
        self.num_iterations = 1000

        self.round = 0
        self.freqs_auction = None
        self.freqs_gem = None
        self.last_state = None
        self.players = None

        self.init()

    def init(self):
        self.freqs_auction = list(AUCTIONS)
        self.freqs_gem = list(GEMS)
        self.players = []
        for _ in range(self.n):
            p = MinimumPlayerState(
                coins=SETUP[self.n][0],
                collection=[0 for _ in range(len(GEMS))],
            )
            self.players.append(p)

    def update_state(self, state):
        # print(self.freqs_auction, self.freqs_gem, "***")
        self.freqs_auction[state.auction] -= 1
        if self.round == 0:
            for gem in state.gems:
                self.freqs_gem[gem] -= 1

        wid = state.last_auction.wid
        if wid != None:
            ls = self.last_state
            la = state.last_auction
            bid = la.bids[la.wid]
            match ls.auction:
                case 0:
                    self.players[wid].coins -= bid
                    self.players[wid].collection[ls.gems[1]] += 1
                    self.freqs_gem[ls.gems[1]] -= 1

                case 1:
                    self.players[wid].coins -= bid
                    for gem in ls.gems:
                        self.players[wid].collection[gem] += 1
                        self.freqs_gem[gem] -= 1

                case 2:
                    self.players[wid].coins += 10 - bid
                    self.players[wid].loans += 10
                case 3:
                    self.players[wid].coins += 20 - bid
                    self.players[wid].loans += 20
                case 4:
                    self.players[wid].coins -= bid
                    self.players[wid].invests += bid + 5
                case 5:
                    self.players[wid].coins -= bid
                    self.players[wid].invests += bid + 10

    def bid(self, state):
        self.update_state(state)

        root = Node()
        root.init_from_player(self, state)
        for _ in range(self.num_iterations):
            node = self.select(root)
            if not node.ended():
                node = self.expand(node)
        bid = super().bid(state)

        self.last_state = state
        self.round += 1
        return bid

    def bid_z(self, state):
        root = Node(state)
        for _ in range(self.num_iterations):
            node = self._select(root)
            if not node.is_terminal():
                node = self._expand(node)
            result = self._simulate(node)
            self._backpropagate(node, result)
        return self._best_action(root)

    def select(self, node):
        while node.fully_expanded() and not node.ended():
            node = node.best_child(self.exploration)
        return node

    def expand(self, node):
        child = Node()
        child.init_from_expand(node)
        child.game.play()

        node.children[0].append(child)
        return child

    def _simulate(self, node):
        state = node.state.copy()
        while not state.is_terminal():
            my_action = random.randint(0, state.budgets[0])
            opp_action = state.sample_opponent_bid()
            card_value = state.sample_card()
            state = state.apply(my_action, opp_action, card_value)
        return 1 if state.winner() == 0 else 0

    def _best_action(self, root):
        # collapse 2D children down to best bid by total visits across card outcomes
        bid_visits = []
        for bid, row in enumerate(root.children):
            total = sum(c.visits for c in row if c is not None)
            bid_visits.append((bid, total))
        best_bid, _ = max(bid_visits, key=lambda x: x[1])
        return best_bid
