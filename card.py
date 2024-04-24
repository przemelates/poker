import random
COLOURS = {"♦" : "Diamonds", "♥" : "Hearts","♣" : "Clubs", "♠" : "Spades"}
VALUES = {2: "Two", 3: "Three", 4:"Four", 5:"Five", 6:"Six", 7:"Seven", 8:"Eight", 9:"Nine", 10:"Ten", 11:"Jack", 12:"Queen", 13:"King", 14:"Ace"}
VALUES_STR = dict(zip(list(VALUES.keys()),[i for i in "23456789TJQKA"]))
SUITS_COLOR = {"♦" : "\033[34m",  "♥" : "\033[31m", "♣" : "\033[33m", "♠" : "\033[32m"}

class Card:
    suit : str
    value : int
    def __init__(self,suit,value) -> None:
        if suit not in COLOURS.keys() or value not in VALUES.keys():
            print("Not a valid card")
        else:
            self.suit = suit
            self.value = value

    def __str__(self) -> str:
        return f"{SUITS_COLOR[self.suit]}{VALUES[self.value]}  of  {COLOURS[self.suit]}\033[39m "
    def __repr__(self) -> str:
        return f"{SUITS_COLOR[self.suit]}{VALUES_STR[self.value]}{self.suit}\033[39m "

class Deck:
    deck : list[Card] = list()
    def __init__(self):
        for i in VALUES.keys():
            for j in COLOURS.keys():
                self.deck.append(Card(j,i))
    
    def deal_cards(self,no):
        for i in range(no):
            card = random.choice(self.deck)
            self.deck.remove(card)
            yield card

