from __future__ import annotations
from time import sleep
import copy
import os
from itertools import cycle, dropwhile
from typing import Callable

from dataclasses import dataclass
from cards import *
from handevaluator import *


@dataclass
class Player:
    name: str
    chips: int = 1000
    is_active: bool = True
    can_react: bool = True
    is_dealer: bool = False
    cards: list[Card] | None = None

    def __hash__(self):
        return self.name.__hash__()


class Game:
    def __init__(self, players: list[Player], configuration=None) -> None:
        self.time = 0
        self.ante = 10
        self.small_blind_value = 20
        self.big_blind_value = 40

        self.players = players
        self.players[0].is_dealer = True
        self.controlled_player = players[0]
          
    def display_players(self):
        for p in self.players:
            print(p.name)

    def iterate_players(self):
        cycled = cycle(self.players)
        dropped = dropwhile(lambda p: not p.is_dealer, cycled)
        for player in dropwhile(lambda p: not p.is_active, dropped):
            yield player

    def start(self):
        round = Round(self)
        round.start()
        print("Play again?")


@dataclass
class Option:
    name: str
    hotkey: str
    action: Callable
    is_breaking: bool = True

    def __hash__(self):
        return self.name.__hash__()


class Round:
    round_phases = ["Pre-bets", "Flop", "Turn", "River"]

    def __init__(self, game):
        self.round_phase = 1
        self.pot = 0
        self.game = game
        self.deck = Deck()
        self.community_cards = []
        self.options = {
            "k": Option("Check", "C", self.check),
            "c": Option("Call", "C", self.call),
            "x": Option("All-in", "X", self.fold),
            "f": Option("Fold", "F", self.all_in),
            "b": Option("Bet", "", lambda: None),
            "h": Option("History", "H", self.history, is_breaking=False)
        }

        self.bets = {p: 0 for p in self.game.players}
        self.log = []
        self.yakus = {p: None for p in self.game.players}


        for player in self.game.players:
            player.cards = self.deck.deal_many(2)

    def get_max_bet(self):
        return max(self.bets.values())

    def start(self):
        print("Round begins...")
        while True:
            for player in self.game.iterate_players():
                if all((not p.can_react for p in self.game.players)):
                    break

                self.interface(player)

                while True:
                    opts = self.get_options(player)
                    options = {self.options[opt].hotkey: self.options[opt] for opt in opts}
                    ask_string = "Press " + ", ".join([f"{key} to {option.name}" for key, option in options.items()])
                    ", or enter the amount of your bet"
                    user_input = input(ask_string).upper()

                    if user_input in options.keys():
                        options[user_input].action(player)
                    elif all((char in '0123456789' for char in user_input)):
                        size = int(user_input)
                        if player.chips < size or size <= self.get_max_bet() - self.bets[player]:
                            print("Inadmissible bet size")
                            continue
                        self.take_bet(player, size)
                        self.log.append(f"{player.name} bets {size}")
                        break

                    else:
                        print("Inadmissible action")
                        continue

                    if options[user_input].is_breaking:
                        player.can_react = False
                        break

            end = self.next_phase()
            if end:
                break

    def get_options(self, player):
        max_bet = self.get_max_bet()
        if self.bets[player] == max_bet:
            opts = "kbxh"
        elif self.bets[player] < max_bet and player.chips > max_bet - self.bets[player]:
            opts = "cbxfh"
        else:
            opts = "xfh"
        return opts

    def next_phase(self):
        print("Moving onto the next round phase...")
        self.bets = {p: 0 for p in self.game.players}
        for player in self.game.players:
            player.can_react = True

        self.round_phase += 1
        if self.round_phase == 2:
            cards = self.deck.deal_many(3)
        elif self.round_phase == 3 or self.round_phase == 4:
            cards = self.deck.deal_many(1)
        else:
            self.showdown()
            return True

        self.community_cards.extend(cards)
        self.log.append(f"Dealer reveals {' '.join((str(c) for c in cards))}")
        return False

    def take_bet(self, player: Player, amount: int):
        player.chips -= amount
        self.bets[player] += amount
        self.pot += amount

    def check(self, player: Player):
        self.log.append(f"{player.name} checks")

    def call(self, player: Player):
        amount = self.get_max_bet() - self.bets[player]
        self.log.append(f"{player.name} calls {amount}")
        self.take_bet(player, amount)

    def fold(self, player: Player):
        self.log.append(f"{player.name} folds")
        player.is_active = False

    def all_in(self, player: Player):
        self.log.append(f"{player.name} is all-in for {player.chips} more")
        self.take_bet(player, player.chips)
        player.is_active = False

    def history(self, player):
        for entry in self.log:
            print(entry)

    def showdown(self):
        print("SHOWDOWN!")
        print(f"Community cards: {Card.str_list(self.community_cards)}")
        for player in self.game.players:
            if not player.is_active:
                continue
            self.yakus[player] = HandEvaluator.evaluate(player.cards + self.community_cards)
            print(f"{player.name} has {Card.str_list(player.cards)} which makes a {self.yakus[player]}.")

        winner = max(self.yakus, key=self.yakus.get)
        print(f"{winner.name} wins pot! ({self.pot})")
        winner.chips += self.pot

    def interface(self, player: Player):
        print(
        '----------------------------------------' + '\n'
        + "SKAWINA HOLD'EM" + '\n' 
        )
        print(f"Your cards: {' '.join((str(card) for card in player.cards))}" )
        print(f"Community cards: {self.community_cards}"+'\n')
        self.history(player)

        print(f"POT:{self.pot}")
        print(f"Current player: {player.name}")
        print(
        '----------------------------------------' + '\n'
        )




if __name__ == '__main__':
    i = 0
    player_names = ["Roe", "Janus", "Szynek"]
    players = [Player(name) for name in player_names]
    game = Game(players)
    game.start()









     

    

        

