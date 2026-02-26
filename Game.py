import random
from Materials import GEMS, SETUP, AUCTIONS, VALUE_CHART
from bisect import bisect_left
from Models import LastAuction, ObservedState, PlayerState
from copy import deepcopy


class Game:
    def render(self):
        return
        print(self.deck_auction)
        print(self.deck_gem)
        input("+++++")
        pass

    def __init__(self, players, deck_auction_template, deck_gem_template):
        #
        self.deck_auction = None
        self.deck_gem = None
        self.last_auction = None
        self.players = None
        self.winners = None

        #
        self.deck_auction = self.create_deck(deck_auction_template)
        self.deck_gem = self.create_deck(deck_gem_template)
        self.last_auction = LastAuction()
        n = len(players)
        self.players = []
        for pid in range(n):
            hand = [self.deck_gem.pop() for _ in range(SETUP[n][1])]
            player = PlayerState(
                model=players[pid](n, pid, deepcopy(hand)),
                coins=SETUP[n][0],
                hand=hand,
                collection=[0 for _ in range(len(deck_gem_template))],
            )
            self.players.append(player)

        #
        self.render()
        while True:
            self.play()
            self.render()
            if self.winners != None:
                break

    def play(self):
        # get bids
        state = ObservedState(
            auction=self.deck_auction[-1],
            gems=self.deck_gem[-2:],
            last_auction=self.last_auction,
        )
        bids = [p.model.bid(state) for p in self.players]

        # get winners
        auction = self.deck_auction[-1]
        max_bid = float("-inf")
        wids = []
        for pid, bid in enumerate(bids):
            limit_bid = self.players[pid].coins + (
                10 if auction == 2 else 20 if auction == 3 else 0
            )
            if not (0 <= bid <= limit_bid):
                raise
            if bid > max_bid:
                max_bid = bid
                wids = [pid]
            elif bid == max_bid:
                wids.append(pid)

        # tiebreak
        if len(wids) == 1:
            wid = wids[0]
        elif self.last_auction.wid != None:
            wid = wids[(bisect_left(wids, self.last_auction.wid) - 1) % len(wids)]
        else:
            wid = random.choice(wids)

        # resolve
        match auction:
            case 0:
                self.players[wid].coins -= max_bid
                self.collect(wid)
            case 1:
                self.players[wid].coins -= max_bid
                self.collect(wid)
                self.collect(wid)
            case 2:
                self.players[wid].coins += 10 - max_bid
                self.players[wid].loans += 10
            case 3:
                self.players[wid].coins += 20 - max_bid
                self.players[wid].loans += 20
            case 4:
                self.players[wid].coins -= max_bid
                self.players[wid].invests += max_bid + 5
            case 5:
                self.players[wid].coins -= max_bid
                self.players[wid].invests += max_bid + 10

        # check end
        if len(self.deck_gem) == 0:
            self.end()
            return

        # update last auction
        self.last_auction.bids = bids
        self.last_auction.wid = wid
        if self.players[wid].hand:
            reveal_id = self.players[wid].model.reveal(bids)
            gem = self.players[wid].hand.pop(reveal_id)
            self.last_auction.reveal = gem
        else:
            self.last_auction.reveal = None

        # update deck
        self.deck_auction.pop()

    def end(self):
        gem_counts = [0 for _ in range(len(GEMS))]
        for p in self.players:
            for gem in p.hand:
                gem_counts[gem] += 1
        gem_values = [VALUE_CHART[count] for count in gem_counts]

        max_score = float("-inf")
        wids = []
        for i, p in enumerate(self.players):
            score = (
                sum([gem_values[gem] * count for gem, count in enumerate(p.collection)])
                + p.coins
                - p.loans
                + p.invests
            )

            if score > max_score:
                max_score = score
                wids = [i]
            elif score == max_score:
                wids.append(i)
        self.winners = wids

    def collect(self, pid):
        try:
            gem = self.deck_gem.pop()
            self.players[pid].collection[gem] += 1
        except:
            pass

    def create_deck(self, template):
        deck = [i for i, count in enumerate(template) for _ in range(count)]
        random.shuffle(deck)
        return deck
