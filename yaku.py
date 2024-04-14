from __future__ import annotations
from dataclasses import dataclass, field
from cards import *


@dataclass
class Yaku:
    high_card: Card = Card()
    second_high_card: Card | None = None
    kickers: list[Card] = field(default_factory=lambda: [])  # wtf
    base_value: int = 0

    def __gt__(self, other):
        if self.base_value != other.base_value:
            return self.base_value > other.base_value

        if self.high_card != other.high_card:
            return self.high_card > other.high_card

        if self.second_high_card is not None and self.second_high_card != other.second_high_card:
            return self.second_high_card > other.second_high_card

        for k1, k2 in zip(self.kickers, other.kickers):
            if k1 == k2:
                continue
            return k1 > k2

    def _kickers_str(self):
        return "-".join(map(lambda c: str(c.value), self.kickers))


@dataclass
class SuitYaku(Yaku):
    suit: int = 0

    def suit_str(self):
        return ["Spades", "Hearts", "Diamonds", "Clubs"][self.suit]


@dataclass
class RoyalFlush(SuitYaku):
    base_value = 10

    def __str__(self):
        return f"Royal Flush in {self.suit}"


@dataclass
class StraightFlush(SuitYaku):
    base_value = 9

    def __str__(self):
        return f"Straight Flush in {self.suit}, {self.high_card.value} high"


@dataclass
class Quads(Yaku):
    base_value = 8

    def __str__(self):
        return f"Quad {self.high_card.value}'s, {self.kickers[0].value} kicker"


@dataclass
class FullHouse(Yaku):
    base_value = 7

    def __str__(self):
        return f"Full House, {self.high_card.value}'s and {self.second_high_card.value}'s"


@dataclass
class Flush(SuitYaku):
    base_value = 6

    def __str__(self):
        return f"Flush in {self.suit}, {self.high_card.value} high"


@dataclass
class Straight(Yaku):
    base_value = 5

    def __str__(self):
        return f"Straight, {self.high_card.value} high"


@dataclass
class Set(Yaku):
    base_value = 4

    def __str__(self):
        return f"Set of {self.high_card.value}'s, {self._kickers_str()} kickers"


@dataclass
class TwoPair(Yaku):
    base_value = 3

    def __str__(self):
        return f"Two Pair, {self.high_card.value}'s and {self.second_high_card.value}'s, {self.kickers[0].value} kicker"


@dataclass
class Pair(Yaku):
    base_value = 2

    def __str__(self):
        return f"Pair of {self.high_card.value}'s, {self._kickers_str()} kickers"


@dataclass
class HighCard(Yaku):
    base_value = 1

    def __str__(self):
        return f"High Card {self.high_card.value}, {self._kickers_str()} kickers"
