from time import sleep
import threading
import copy
import random
import re
import os

from cards import *
from handevaluator import *


class Game:
    def __init__(self, players, configuration=None) -> None:
        self.time = 0
        self.ante = 10
        self.small_blind = [20, 0]  # [value, playerId]
        self.big_blind = [40, 1]  # ditto
        self.dealer = 0

        self.players = set(players)  # adds all immediately
        self.controlled_player = players[0]
        self.balances = {p: 1000 for p in self.players}  # python magic!
         
    def display_time(self):
        while True:
            sleep(1)
            self.time += 1
            print(self.time)
          
    def display_players(self):
         for i in self.players:
              print(i)


class Round:
    round_phases = {1: "Pre-bets", 2: "Flop", 3: "Turn", 4: "River"}
    community_cards = set()
    round_phase = 1
    players = list()
    pot = 0
    player_cards = dict()
    bets = dict()
    balances = dict()


    def __init__(self, game) -> None:
        super().__init__()
        self.game = game
        self.current_player = game.dealer
        print("Round begins...")
        game.ante *= 2
        self.players = list(game.players)
        self.balances = game.balances
        self.balances[self.players[game.big_blind[1]]] -= game.big_blind[0]
        self.balances[self.players[game.small_blind[1]]] -= game.small_blind[0]
        for i in self.players:
            self.balances[i] -= game.ante
        self.pot = 0

        self.deck = Deck()
        self.player_cards = {player: self.deck.deal_many(2) for player in self.players}
        self.bets = {player: 0 for player in self.players}

        self.bets_phases = dict(zip(list(Round.round_phases.keys()), [copy.deepcopy(self.bets) for i in range(len(Round.round_phases.keys()))]))
        self.bets[self.players[game.small_blind[1]]] += game.small_blind[0]
        self.bets[self.players[game.big_blind[1]]] += game.big_blind[0]
        self.bets_phases[1][self.players[game.small_blind[1]]] += game.small_blind[0]
        self.bets_phases[1][self.players[game.big_blind[1]]] += game.big_blind[0]
        self.next_move()
        

    ### Misc tools ###
    def get_next_player(self,player):   # Returns ID
        if player != len(self.players) -1:
            return player +1
        else:
            return 0
    
    def get_previous_player(self,player): # Ditto
        if player != 0:
            return player - 1
        else:
            return len(self.players) - 1
        
    def get_player_by_id(self,id):
        return self.players[id]


    ### Round course and administration ###
    def next_player(self):
        if self.current_player!=len(self.players)-1:
            self.current_player+=1
        else:
            self.current_player = 0

    def next_move(self, *args):
        self.Interface(args)
        bets = [i for i in self.bets_phases[self.round_phase].values()]
        if (i == j for i,j in bets) and (0 not in bets):
            self.round_phase +=1
            print("Moving onto the next round phase...")
            if self.round_phase == 2:
                self.community_cards.add(self.deck.deal_many(3))
            elif self.round_phase == 3 or self.round_phase ==4:
                self.community_cards.add(self.deck.deal_card())
            else:
                self.showdown()

        elif self.bets[self.players[self.current_player]] < max(bets):
            input1 = input("Press C to call, F to fold, X to all-in or enter the amount of your bet" + '\n').upper()
            if input1 == "C":
                self.call(self.current_player, self.bets_phases[self.round_phase][self.get_player_by_id(self.get_previous_player(self.current_player))]- self.bets_phases[self.round_phase]
                          [self.get_player_by_id(self.current_player)])
            elif input1 == "F":
                self.fold(self.current_player)
            elif input1 == "X":
                self.bet(self.current_player, self.balances[self.get_player_by_id(self.current_player)])
            elif (i in r'[0-9]' for i in input1):
                self.bet(self.current_player, int(input1))
            else:
                self.next_move("Inadmissible action")


        
        else:
            input1 = input("Press C to check, X to all-in or enter the amount of your bet"+ '\n')
            if input1 == "C":
                self.call(self.current_player, self.bets_phases[self.round_phase][self.get_player_by_id(self.get_previous_player(self.current_player))]- self.bets_phases[self.round_phase]
                          [self.get_player_by_id(self.current_player)])
            elif input1 == "X":
                self.bet(self.current_player, self.balances[self.get_player_by_id(self.current_player)])
            elif (i in r'[0-9]' for i in input1):
                self.bet(self.current_player, int(input1))
            else:
                self.next_move("Inadmissible action")


    def bet(self,player,amount):
        if self.balances[self.players[player]]>=amount:
            self.balances[self.get_player_by_id(player)] -= amount
            self.bets[self.players[player]] +=amount
            self.bets_phases[self.round_phase][self.players[player]] += amount
            self.pot += amount
            self.next_player()
            self.next_move(f"{self.get_player_by_id(player)} has bet {amount}")
        else:
            self.next_move("Inadmissible bet size")
    
    call = bet

    def check(self,player):

        self.next_player()
        self.next_move(f"{self.get_player_by_id(player)} has checked")

    def fold(self,player):
        self.balances[self.players[player]] -= self.bets[self.players[player]]
        self.next_player()
        self.players.remove(self.get_player_by_id(player))
        if len(self.players) == 1:
            os.abort()
        self.next_move(f"{self.get_player_by_id(player)} has folded")

    def update_balances(self):
        self.game.balances = self.balances

    def showdown(self):
        self.game.big_blind[0] *=2
        self.game.small_blind[1] *=2
        self.game.big_blind[1] = self.get_next_player(self.game.big_blind[1])
        self.game.small_blind[1] = self.get_next_player(self.game.small_blind[1])

    ##############################################
    
    def Interface(self, *args):
        print(
        '----------------------------------------' + '\n'
        + "SKAWINA HOLD'EM" + '\n' 
        )
        print(f"Your cards: {(self.player_cards[self.get_player_by_id(0)])}" )
        print(f"Community cards: {self.community_cards}"+'\n')
        for i in self.players:
            print(f"{i}: {self.balances[i]}, bets {self.bets[i]}")
            if i == self.players[self.game.big_blind[1]]:
                print(" *BIG BLIND*" +'\n')
            elif i == self.players[self.game.small_blind[1]]:
                print(" *SMALL BLIND*"+'\n')
            elif i == self.players[self.game.dealer]:
                print(" *DEALER*"+'\n')
            else:
                print('\n')
        print(f"POT:{self.pot}")
        print(f"Current player: {self.get_player_by_id(self.current_player)}")
        print(
        '----------------------------------------' + '\n' 
        )
        if len(args) !=0:
            for i in args:
                print(f"Attention:{str(i)}")



if __name__ == '__main__':
    i = 0
    players = ["Roe", "Janus", "Szynek"]

    game = Game(players)
    round = Round(game)









     

    

        

