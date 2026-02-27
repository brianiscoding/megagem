from Models import GameState, PlayerState, Log, Settings
from Materials import SETUP
import random

from bisect import bisect_left


def create_deck(freqs):
    deck = [i for i, count in enumerate(freqs) for _ in range(count)]
    random.shuffle(deck)
    return deck


def init_game(freqs_auction, freqs_gem, value_chart, player_models):
    g = GameState()
    g.settings = Settings(
        freqs_auction=freqs_auction, freqs_gem=freqs_gem, value_chart=value_chart
    )
    g.deck_auction = create_deck(freqs_auction)
    g.deck_gem = create_deck(freqs_gem)
    g.auction = g.deck_auction.pop()
    g.gems = [g.deck_gem.pop() for _ in range(2)]
    g.logs = []

    n = len(player_models)
    g.players = []
    for pid, model in enumerate(player_models):
        hand = [g.deck_gem.pop() for _ in range(SETUP[n][1])]
        p = PlayerState(
            model=model(g, pid),
            coins=SETUP[n][0],
            loans=0,
            invests=0,
            hand=hand,
            collection=[0 for _ in range(len(freqs_gem))],
        )
        g.players.append(p)
    return g


def end(g):
    if g.winners:
        return

    gem_counts = list(g.settings.freqs_gem)
    for p in g.players:
        for i, count in enumerate(p.collection):
            gem_counts[i] -= count
    gem_values = [g.settings.value_chart[count] for count in gem_counts]

    max_score = float("-inf")
    wids = set()
    for i, p in enumerate(g.players):
        score = (
            sum([gem_values[gem] * count for gem, count in enumerate(p.collection)])
            + p.coins
            - p.loans
            + p.invests
        )
        g.players[i].score = score

        if score > max_score:
            max_score = score
            wids = set([i])
        elif score == max_score:
            wids.add(i)
    g.winners = wids


def rollout(g):
    while not g.winners:
        play(g)


def play(g):
    if g.winners:
        return

    # get bids
    auction = g.auction
    max_bid = float("-inf")
    wids = []
    bids = []
    for pid, p in enumerate(g.players):
        limit_bid = p.coins + (10 if auction == 2 else 20 if auction == 3 else 0)
        bid = p.model.bid(limit_bid)
        bids.append(bid)
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
    elif len(g.logs) != 0:
        wid = wids[(bisect_left(wids, g.logs[-1].wid) - 1) % len(wids)]
    else:
        wid = random.choice(wids)

    # resolve bids
    match auction:
        case 0:
            g.players[wid].coins -= max_bid
            gem = g.gems.pop()
            g.players[wid].collection[gem] += 1
        case 1:
            g.players[wid].coins -= max_bid
            gem = g.gems.pop()
            g.players[wid].collection[gem] += 1
            if g.gems:
                gem = g.gems.pop()
                g.players[wid].collection[gem] += 1
        case 2:
            g.players[wid].coins += 10 - max_bid
            g.players[wid].loans += 10
        case 3:
            g.players[wid].coins += 20 - max_bid
            g.players[wid].loans += 20
        case 4:
            g.players[wid].coins -= max_bid
            g.players[wid].invests += max_bid + 5
        case 5:
            g.players[wid].coins -= max_bid
            g.players[wid].invests += max_bid + 10
    g.auction = None

    # get reveal if able, then update logs
    hand = g.players[wid].hand
    if hand:
        gem = g.players[wid].model.reveal(hand, bids)
        if gem not in hand:
            raise
        gem = g.players[wid].hand.remove(gem)
        g.logs.append(Log(bids=bids, wid=wid, reveal=gem))
    else:
        g.logs.append(Log(bids=bids, wid=wid, reveal=None))

    # check end
    if len(g.deck_gem) == len(g.gems) == 0:
        end(g)
        return

    # replenish
    g.auction = g.deck_auction.pop()
    try:
        match auction:
            case 0:
                g.gems.insert(0, g.deck_gem.pop())
            case 1:
                g.gems.insert(0, g.deck_gem.pop())
                g.gems.insert(0, g.deck_gem.pop())
    except:
        pass
