from __future__ import annotations

from cards import *
from yaku import *
from dataclasses import dataclass
from collections.abc import Iterable


"""
Hand strength evaluation
"""


class HandEvaluator:
    """
    Helper private methods
    """
    @staticmethod
    def _longest_suit(hand: list[Card]) -> list[Card]:
        suit_count = [0 for _ in CARD_SUITS]
        for card in hand:
            suit_count[card.suit] += 1
        best_suit = suit_count.index(max(suit_count))
        return list(filter(lambda c: c.suit == best_suit, hand))

    @staticmethod
    def _check_straight_5(hand: list[Card], start_index: int) -> bool:
        value = hand[start_index].value
        for i in range(5):
            if hand[start_index + i].value != value:
                return False
            value += 1

        return True

    @staticmethod
    def _highest_index(arr, el):
        for i, e in list(enumerate(arr))[::-1]:
            if e == el:
                return i

    """
    Yaku check methods
    """
    @staticmethod
    def check_straight_flush(hand: list[Card]) -> Yaku | None:
        longest_suit = HandEvaluator._longest_suit(hand)
        longest_suit.sort()
        for i in range(len(longest_suit) - 4):
            if HandEvaluator._check_straight_5(longest_suit, i):
                if longest_suit[i + 4].value == 12:
                    return RoyalFlush(suit=longest_suit[0].suit)
                return StraightFlush(high_card=longest_suit[i + 4], suit=longest_suit[0].suit)

    @staticmethod
    def check_flush(hand: list[Card]) -> Yaku | None:
        longest_suit = HandEvaluator._longest_suit(hand)
        if len(longest_suit) < 5:
            return None
        return Flush(high_card=max(longest_suit), suit=longest_suit[0].suit)

    @staticmethod
    def check_straight(_hand: list[Card]) -> Yaku | None:
        hand = list(set(_hand))
        hand.sort()

        for i in range(len(hand) - 4):
            if HandEvaluator._check_straight_5(hand, i):
                return Straight(high_card=hand[i + 4])

    @staticmethod
    def check_multiples(hand: list[Card]) -> Yaku | None:
        multiples = [0] * 13
        for card in hand:
            multiples[card.value] += 1

        if 4 in multiples:
            high_card = Card(-1, multiples.index(4))
            kickers = [max(filter(lambda c: c != high_card, hand))]
            return Quads(high_card=high_card, kickers=kickers)

        if 3 in multiples and 2 in multiples:
            set_card = Card(-1, multiples.index(3))
            pair_card = Card(-1, HandEvaluator._highest_index(multiples, 2))
            return FullHouse(high_card=set_card, second_high_card=pair_card)

        if 3 in multiples:
            set_card = Card(-1, multiples.index(3))
            kickers = sorted(filter(lambda c: c != set_card, hand), reverse=True)[:2]     # 2 kickers with a set
            return Set(high_card=set_card, kickers=kickers)

        if multiples.count(2) >= 2:
            first_pair_card = Card(-1, HandEvaluator._highest_index(multiples, 2))
            multiples.pop(first_pair_card.value)
            second_pair_card = Card(-1, HandEvaluator._highest_index(multiples, 2))
            kickers = [max(filter(lambda c: c != first_pair_card and c != second_pair_card, hand))]
            return TwoPair(high_card=first_pair_card, second_high_card=second_pair_card, kickers=kickers)

        if 2 in multiples:
            pair_card = Card(-1, multiples.index(2))
            kickers = sorted(filter(lambda c: c != pair_card, hand), reverse=True)[:3]    # 3 kickers with a pair
            return Pair(high_card=pair_card, kickers=kickers)

    @staticmethod
    def check_high_card(hand: list[Card]) -> Yaku:
        top5 = sorted(hand, reverse=True)[:5]
        return HighCard(high_card=top5[0], kickers=top5[1:])

    @staticmethod
    def evaluate(hand: list[Card]) -> Yaku:
        methods = [
            HandEvaluator.check_straight_flush,
            HandEvaluator.check_flush,
            HandEvaluator.check_straight,
            HandEvaluator.check_multiples
        ]

        for method in methods:
            yaku = method(hand)
            if yaku is not None:
                return yaku

        return HandEvaluator.check_high_card(hand)


if __name__ == '__main__':
    print("Hand Evaluator Tests")

    def hand_from_str(s):
        return [Card.from_str(ss) for ss in s.split(" ")]

    test_data = [
        ("As Qs Kh 4s Js Ts Ks", "Royal Flush in Spades"),
        ("Ks Kh Kd Jh Qh 9h Th", "Straight Flush in Hearts, K high"),
        ("5h 6h 7h 5s 5d 8h 5c", "Quad 5's, 8 kicker"),
        ("7h 9s Jc 7c 9c 9d Jh", "Full house, 9's and J's"),
        ("7c 9c Kc 9h Qc 9d 2c", "Flush in Clubs, K high"),
        ("Jd 5s 6c 7d 8h Ts 9c", "Straight, J high"),
        ("8h Jd Qd 7h Js Ad Jh", "Set of J's, A-Q kicker"),
        ("8h Jd Qd 8c Js Ad Ah", "Two Pair, A's and J's, Q kicker"),
        ("8h Jd Qd 5c Js Ad 3h", "Pair of J's, A-Q-8 kicker"),
        ("8h Jd Qd 6c Ks 2d 3h", "High Card K, Q-J-8-6 kicker"),
    ]

    print(f"{'HAND':45}{'EVALUATED':45}{'EXPECTED':45}")
    for test in test_data:
        test_hand = hand_from_str(test[0])
        yaku = HandEvaluator.evaluate(test_hand)
        print(f"{test[0]:45}{str(yaku):45}{test[1]:45}")
