from dataclasses import dataclass
from itertools import product
from random import randint


CARD_SUITS = range(3)
CARD_VALUES = range(13)
CARD_VALUES_HONORS = range(8, 13)


@dataclass
class Card:
    suit: int
    value: int

    @staticmethod
    def from_str(s: str):
        suit = "shdc".index(s[1])
        value = "23456789TJQKA".index(s[0].upper())
        return Card(suit, value)

    """
    Defines the string representation of a card, called by print()
    """
    def __str__(self):
        return "♠♥♦♣"[self.suit] + "23456789TJQKA"[self.value + 2]

    def __repr__(self):
        return "♠♥♦♣"[self.suit] + "23456789TJQKA"[self.value + 2]

    def value_str(self):
        return "23456789TJQKA"[self.value + 2]


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
