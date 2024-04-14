from dataclasses import dataclass
from itertools import product
from random import randint


CARD_SUITS = range(4)
CARD_VALUES = range(13)
CARD_VALUES_HONORS = range(8, 13)
SUITS_SHORT = "♠♥♦♣"
SUITS_LONG = ["Spades", "Hearts", "Diamonds", "Clubs"]
CARD_VALUES_STR = "23456789TJQKA"


class Suit(int):
    def __repr__(self):
        if self.real == -1:
            return ""
        return SUITS_SHORT[self.real]

    def __str__(self):
        return SUITS_SHORT[self.real]


class Value(int):
    def __repr__(self):
        return CARD_VALUES_STR[self.real]

    def __str__(self):
        return CARD_VALUES_STR[self.real]


class Card:
    def __init__(self, suit=0, value=0):
        if isinstance(suit, int):
            suit = Suit(suit)
        if isinstance(value, int):
            value = Value(value)

        self.suit = suit
        self.value = value

    @staticmethod
    def from_str(s: str):
        suit = "shdc".index(s[1])
        value = "23456789TJQKA".index(s[0].upper())
        return Card(Suit(suit), Value(value))

    """
    Defines the string representation of a card, called by print()
    """
    def __str__(self):
        return SUITS_SHORT[self.suit] + CARD_VALUES_STR[self.value]

    def __repr__(self):
        return str(self.suit) + str(self.value)

    """
    Comparison operations overrides.
    Assuming only the value of a card matters.
    """
    def __eq__(self, other):
        if isinstance(other, int):
            return self.value == other
        return self.value == other.value

    def __lt__(self, other):
        if isinstance(other, int):
            return self.value < other
        return self.value < other.value

    def __hash__(self):
        return (self.value + self.suit * 13).__hash__()


class DeckEmptyError(Exception):
    pass


class Deck:
    def __init__(self):
        self._deck = [Card(s, v) for s, v in product(range(4), range(13))]

    def deal_card(self):
        if len(self._deck) == 0:
            raise DeckEmptyError("There are no more cards in the deck!")

        index = randint(0, len(self._deck) - 1)
        card = self._deck.pop(index)
        return card

    def deal_many(self, n):
        return [self.deal_card() for _ in range(n)]