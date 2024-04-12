from __future__ import annotations

from cards import *
from dataclasses import dataclass

"""
Hand strength evaluation
"""


@dataclass
class Yaku:
    yaku: str
    high_card: Card | None

    def __str__(self):
        if self.high_card is None:
            return self.yaku
        return f"{self.yaku}, {self.high_card.value_str()} high"


class HandEvaluator:
    @staticmethod
    def check_flush(hand: list[Card]) -> Yaku | None:
        suit_count = [0 for _ in CARD_SUITS]
        for card in hand:
            suit_count[card.suit] += 1

        if max(suit_count) < 5:
            return None

        best_suit = suit_count.index(max(suit_count))
        high_card = max([c for c in hand if c.suit == best_suit], key=lambda c: c.value)
        return Yaku("Flush", high_card)

    @staticmethod
    def check_straight(hand: list[Card]) -> Yaku | None:
        flush_array = hand
        flush_array.sort(key=lambda c: c.value)  # Sort by first element
        streak = 1
        excluded = set()
        for i in range(len(flush_array) - 1, 0, -1):
            if flush_array[i].value == flush_array[i - 1].value + 1:
                streak += 1
                if streak == 5:
                    for i in excluded:
                        flush_array.remove(i)
                    top = max(flush_array, key=lambda c: c.value)
                    return Yaku("Straight", top)
            elif flush_array[i].value == flush_array[i - 1].value:
                continue
            else:
                streak = 1
                excluded.add(flush_array[i])
        return None

    @staticmethod
    def check_straight_flush(hand: list[Card]) -> Yaku | None:
        suit_count = [0 for _ in CARD_SUITS]
        for card in hand:
            suit_count[card.suit] += 1

        if max(suit_count) < 5:
            return None

        best_suit = suit_count.index(max(suit_count))
        hand_best_suit = [card for card in hand if card.suit == best_suit]

        straight = HandEvaluator.check_straight(hand_best_suit)
        if straight is None:
            return None

        return Yaku("Straight Flush", max(hand_best_suit, key=lambda c: c.value))

    @staticmethod
    def check_royal_flush(hand: list[Card]) -> Yaku | None:
        if HandEvaluator.check_straight_flush(hand) is None:
            return None

        royal_flush_sets = []
        for suit in CARD_SUITS:
            royal_flush_set = set()
            royal_flush_sets.append(royal_flush_set)
            for j in CARD_VALUES_HONORS:
                royal_flush_set.add((j, suit))
        for suit in royal_flush_sets:
            if suit in hand:
                return Yaku("Royal Flush", None)
        return None

    @staticmethod
    def check_full(hand: list[Card]) -> Yaku | None:
        # TODO to jest źle!!! trójka zawiera parę
        if HandEvaluator.check_pairs(hand, 3) and HandEvaluator.check_pairs(hand, 2):
            return Yaku("Full House", None)  # TODO high card
        else:
            return None

    @staticmethod
    def get_multiples(hand: list[Card]) -> dict[int, int]:
        count = dict()
        for card in hand:
            if card.value not in count.keys():
                count[card.value] = 1
            else:
                count[card.value] += 1
        return count

    @staticmethod
    def check_pairs(hand, size):
        max_ = max(HandEvaluator.get_multiples(hand).values())
        if max_ != size:
            return False
        values = list(HandEvaluator.get_multiples(hand).values())
        keys = list(HandEvaluator.get_multiples(hand).keys())
        keys.sort(reverse=True)
        for i in range(len(keys)):
            if HandEvaluator.get_multiples(hand)[keys[i]] == size:
                return True, values.count(max_), keys[
                    i]  # How many n-sized card multiples are in hand, what is the highest-value multiplied card

    @staticmethod
    def check_high_card(hand):
        flush_array = list(hand)
        flush_array.sort(key=lambda i: i[0])
        top = max(flush_array, key=lambda i: i[0])
        return top[0]


    """
    Nie ma co sie bawić z ogólnym algorytmem do szukania krotek
    Tutaj lekka duplikacja kodu jest OK bo upraszcza czytanie go
    A python ma być czytelny
    Lepiej zrobić po prostu po jednej metodzie na każdy układ
    """
    # TODO: zrobić tak, a potem uzupełnić metodę poniżej

    @staticmethod
    def better_get_hand_value(hand: list[Card]) -> Yaku:
        methods = [
            HandEvaluator.check_straight_flush,
            HandEvaluator.check_flush,
            HandEvaluator.check_straight,
            HandEvaluator.check_full,
            # TODO ...
        ]

        for method in methods:
            yaku = method(hand)
            if yaku is not None:
                return yaku

        return Yaku("High Card", max(hand, key=lambda c: c.value))

    @staticmethod
    def get_hand_value(self, hand):
        if self.check_royal_flush(hand) == True:
            print("Royal Flush")
            return 140
        elif self.check_straight_flush(hand) != False:
            print(f"Straight Flush, {self.values[self.check_straight_flush(hand)[1]]} high")
            return self.check_straight_flush(hand)[1] + 8 * 14
        elif self.check_pairs(hand, 4) != False:
            print(f"Four of a Kind, {self.values[self.check_pairs(hand, 4)[2]]} high")
            return self.check_pairs(hand, 4)[2] + 7 * 14
        elif self.check_full(hand) != False:
            print(f"Full house, {self.values[self.check_full(hand)[1]]} high")
            return self.check_full(hand)[1] + 0.1 * self.check_full(hand)[2] + 6 * 14
        elif self.check_flush(hand) != False:
            print(f"Flush, {self.values[self.check_flush(hand)[1]]} high")
            return self.check_flush(hand)[1] + 5 * 14
        elif self.check_straight(hand) != False:
            print(f"Straight, {self.values[self.check_straight(hand)[1]]} high")
            return self.check_straight(hand)[1] + 4 * 14
        elif self.check_pairs(hand, 3) != False:
            print(f"Three of a kind, {self.values[self.check_pairs(hand, 3)[2]]} high")
            return self.check_pairs(hand, 3)[2] + 3 * 14
        elif self.check_pairs(hand, 2) != False and self.check_pairs(hand, 2)[1] == 2:
            print(f"Two pairs, {self.values[self.check_pairs(hand, 2)[2]]} high")
            return self.check_pairs(hand, 2)[2] + 2 * 14
        elif self.check_pairs(hand, 2) != False:
            print(f"Pair, {self.values[self.check_pairs(hand, 2)[2]]} high")
            return self.check_pairs(hand, 2)[2] + 14
        else:
            print(f"{self.values[self.check_high_card(hand)]} high")
            return self.check_high_card(hand)