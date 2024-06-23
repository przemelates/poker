import random, copy
from card import*
from hand_evaluation import*

actions = {'C': "call/check", "B": "bet", "F":"Fold"}



def random_action(actions : dict):
    choice : str = random.choice(list(actions.keys()))
    return choice


def charts( hand : list[Card], position : int): ## Position = how many players still to act after you
    assert len (hand) == 2
    ranges = {
    "5": ["AA", "AKo", "AQo", "AJo", "ATo", "AKs", "KK", "KQo", "AQs", "KQs", "QQ", "AJs", "KJs", "QJs", "JJ", "ATs", "KTs", "QTs", "JTs", "TT", "A9s", "T9s", "99", "A8s", "88", "A5s", "A4s", "A3s", "A2s"],
    "2": ["A9o", "A8o", "A7o", "A6o", "A5o", "A4o", "K9o", "Q9o", "J9o", "T9o", "98o", "Q7s", "J7s", "T7s", "Q6s", "T6s", "96s", "Q5s", "85s", "K4s", "64s", "K3s", "53s", "43s", "K2s"],
    "1": ["A3o", "A2o", "K8o", "K7o", "K6o", "K5o", "Q8o", "Q7o", "J8o", "J7o", "T8o", "T7o", "97o", "87o", "86o", "76o", "75o", "J6s", "65o", "64o", "J5s", "T5s", "95s", "54o", "Q4s", "J4s", "T4s", "94s", "84s", "74s", "Q3s", "J3s", "T3s", "73s", "63s", "Q2s", "J2s", "T2s", "52s", "42s", "32s"],
    "4": ["KJo", "QJo", "K9s", "Q9s", "J9s", "K8s", "98s", "A7s", "87s", "77", "A6s", "76s", "66", "65s", "55", "54s", "44"],
    "3": ["KTo", "QTo", "JTo", "Q8s", "J8s", "T8s", "K7s", "97s", "K6s", "86s", "K5s", "75s", "33", "22"],
    "0": ["K4o", "K3o", "K2o", "Q6o", "Q5o", "Q4o", "Q3o", "Q2o", "96o", "95o", "85o", "84o", "74o", "63o", "53o", "52o", "43o", "42o", "93s", "83s", "32o", "92s", "82s", "72s", "62s"],
    "-1": ["J6o", "J5o", "J4o", "J3o", "J2o", "T6o", "T5o", "T4o", "T3o", "T2o", "94o", "93o", "92o", "83o", "82o", "73o", "72o", "62o"]
    }
    hand_str : str
    x  = lambda hand: "s" if hand[0].suit == hand[1].suit else "o"
    if hand[0].value > hand[1].value:
        hand_str = VALUES_STR[hand[0].value] + VALUES_STR[hand[1].value] + x(hand) 
    elif hand[1].value > hand[0].value:
        hand_str = VALUES_STR[hand[1].value] + VALUES_STR[hand[0].value] + x(hand)
    else:
        hand_str = VALUES_STR[hand[0].value] + VALUES_STR[hand[1].value]

    range : int
    for key in ranges.keys():
        if hand_str in ranges[key]:
            range = int(key)

    action : str
    if range >= position:
        action = "B"
    else:
        action = "F"
    return action

print(charts([Card("♦",10),Card("♦",12)], 3))

def hand_strength_evaluator(hand : list[Card], community_cards: list[Card] | None):
    deck = Deck()

    for x in deck.deck:
        for y in hand:
            if x.value == y.value and x.suit == y.suit:
                deck.deck.remove(x)
        for z in community_cards:
            if x.value == z.value and x.suit == z.suit:
                deck.deck.remove(x)
    SAMPLE_SIZE = 300
    winning = list()
    losing = list()
    for i in range(SAMPLE_SIZE):
        deck2 = Deck()
        deck2.deck = deck.deck
        player_hand = list()
        rival_hand = list()
        for a in hand:
            player_hand.append(a)
        for b in deck2.deal_cards(5-len(community_cards)):
            player_hand.append(b)
            rival_hand.append(b)
        for c in deck2.deal_cards(2):
            rival_hand.append(c) 
        if(HandEvaluator.get_hand_value(player_hand))>=HandEvaluator.get_hand_value(rival_hand):
            winning.append(player_hand)
        else:
            losing.append(player_hand)
        
        
    return len(winning)/(len(winning)+len(losing))

##print(hand_strength_evaluator([Card("♦",2),Card( "♥",8)],list()))
           
            



    



