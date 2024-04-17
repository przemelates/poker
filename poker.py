import time, threading, copy, random, re, os
from dataclasses import dataclass
from hand_evaluation import *



@dataclass
class Player:
    name: str
    id: int = 0
    has_folded: bool = False
    cards = list()
    balance: int = 1000
    has_acted =  {p: False for p in range(1,5)} 
    def __hash__(self) -> int:
        return self.name.__hash__()
    def __str__(self) -> str:
        return self.name

players = [Player("Roe"),Player("Janus"),Player("Szynek")]

class Game:
    time = 0
    ante = 10
    small_blind = 20
    big_blind = 40 
    dealer: Player
    controlled_player: Player
 


    def __init__(self, players: list[Player]) -> None:
         self.players = players
         for i in self.players:
            i.id = self.players.index(i)     
         Game.controlled_player = self.players[0]
         self.time = 0
         Game.dealer = self.players[0]
         
    def display_time(self):
        while(True):
            time.sleep(1)
            self.time+=1
            print(self.time)
          
    def display_players(self):
         for i in self.players:
              print(i.name)
        


class Round(Game):

    ### Round-wide variables declaration ###
    colours = {"♦" : "Diamonds", "♥" : "Hearts","♣" : "Clubs", "♠" : "Spades"}
    values = {2: "Two", 3: "Three", 4:"Four", 5:"Five", 6:"Six", 7:"Seven", 8:"Eight", 9:"Nine", 10:"Ten", 11:"Jack", 12:"Queen", 13:"King", 14:"Ace"}
    round_phases = {1:"Pre-flop",2:"Flop",3:"Turn",4:"River"}
    community_cards = set()
    deck = set()
    round_phase = 1
    players: list[Player]
    current_player : Player
    pot = 0
    player_cards = dict()
    bets = dict()

    for i in values.keys():
        for j in colours.keys():
            deck.add((i,j))        # Cards always in format tuple(value,colour)

    def __init__(self, game) -> None:
        print("Round begins...")
        Game.ante *=2
        self.players: list[Player] = game.players
        small_blind = self.get_next_player(game.dealer)
        big_blind = self.get_next_player(self.get_next_player(game.dealer))
        self.current_player = self.get_next_player(big_blind)
        small_blind.balance -= Game.small_blind
        big_blind.balance -= Game.big_blind
        for i in self.players:
            i.balance -= Game.ante
        self.pot = Game.big_blind + Game.small_blind
        for i in self.players:
            for j in Round.draw_cards(2):
                i.cards.append(j)
        self.bets = dict(zip(self.players,[0 for i in range(len(self.players))]))
        self.bets[small_blind] += Game.small_blind
        self.bets[big_blind] += Game.big_blind
        self.next_move()
        

    ### Misc tools ###

    def get_card_name(self,cards):
        names = set()
        for i in cards:
            names.add((self.values[i[0]] + " of " + self.colours[i[1]]))
        return names
    
    def get_next_player(self,player : Player):
        p: Player
        if player.id != len(self.players) -1:
            p = self.players[player.id +1]
            if p.has_folded == True:
                return self.get_next_player(p)
            else:
                return p
        else:
            p = self.players[0]
            if p.has_folded == True:
                return self.get_next_player(p)
            else:
                return p
    
    def get_previous_player(self,player : Player):
        p: Player 
        if player.id != 0:
            p = self.players[player.id - 1]
            if p.has_folded == True:
                self.get_previous_player(p)
            else:
                return p

        else:
            p =  self.players[len(self.players)] - 1
            if p.has_folded == True:
                self.get_previous_player(p)
            else:
                return p

    
    def get_max_bet(self):
        return max(self.bets.values())
        
    def draw_cards(no):
        cards = list()
        deck_copy = copy.deepcopy(Round.deck)
        for i in range(no):
            x = random.choice(list(deck_copy))
            cards.append(x)
            deck_copy.remove(x)
       
        return cards
    
    ### Round course and administration ###

    def next_player(self):
            self.current_player = self.get_next_player(self.current_player)
      

    def next_move(self, *args):
        self.Interface(args)
        bets = list(self.bets.values())
        if ([bets[i] == bets[i+1] for i in range(0,len(bets)-2)] == [True]) and (0 not in bets) and (False not in [p.has_acted[self.round_phase] for p in self.players]): 
            self.round_phase +=1
            print("Moving onto the next round phase...")
            if self.round_phase == 2:
                for i in Round.draw_cards(3):
                    self.community_cards.add(i)
                self.next_move()
            elif self.round_phase == 3 or self.round_phase ==4:
                for i in Round.draw_cards(1):
                    self.community_cards.add(i)
                self.next_move()
            else:
                self.showdown()

        elif self.bets[self.current_player] < self.get_max_bet():
            input1 = input("Press C to call, F to fold, X to all-in or enter the amount of your bet" + '\n')
            if input1 == "C":
                self.call(self.current_player, self.get_max_bet() - self.bets[self.current_player])
            elif input1 == "F":
                self.fold(self.current_player)
            elif input1 == "X":
                self.bet(self.current_player, self.current_player.balance)
            elif (i in r'[0-9]' for i in input1):
                self.bet(self.current_player, int(input1))
            else:
                self.next_move("Inadmissible action")


        
        else:
            input1 = input("Press C to check, X to all-in or enter the amount of your bet"+ '\n')
            if input1 == "C":
                self.check(self.current_player)
            elif input1 == "X":
                self.bet(self.current_player, self.current_player.balance)
            elif (i in r'[0-9]' for i in input1):
                self.bet(self.current_player, int(input1))
            else:
                self.next_move("Inadmissible action")


    def bet(self,player: Player,amount):
        if player.balance >=amount:
            player.balance -= amount
            self.bets[player] +=amount
            self.pot += amount
            player.has_acted[self.round_phase] = True
            self.next_player()
            self.next_move(f"{player} has bet {amount}")
        else:
            self.next_move("Inadmissible bet size")
    
    call = bet

    def check(self,player:Player):
        player.has_acted[self.round_phase] = True
        self.next_player()
        self.next_move(f"{player} has checked")

    def fold(self,player:Player):
        for i in self.round_phases.keys():
            player.has_acted[i] = True
        player.balance -= self.bets[player]
        player.has_folded = True
        del self.bets[player]
        if len(self.players) == 1:
            os.abort()
        self.next_player()
        self.next_move(f"{player} has folded")

    def showdown(self):
        Game.big_blind *=2 
        Game.small_blind *=2
        Game.dealer = self.get_next_player(Game.dealer)

    ##############################################
    
    def Interface(self, *args):
        print(
        '----------------------------------------' + '\n'
        + "SKAWINA HOLD'EM" + '\n' 
        )
        print(f"Your cards: {self.controlled_player.cards}" )
        print(f"Community cards: {self.community_cards}"+'\n')
        for i in self.players:
            if(i.has_folded == False):
                print(f"{i}: {i.balance}, bets {self.bets[i]}")
                if i == self.get_next_player(self.get_next_player(Game.dealer)):
                    print(" *BIG BLIND*" +'\n')
                elif i == self.get_next_player(Game.dealer):
                    print(" *SMALL BLIND*"+'\n')
                elif i == Game.dealer:
                    print(" *DEALER*"+'\n')
                else:
                    print('\n')
            else:
                print(f"{i}: {i.balance} FOLDED")
                if i == self.get_next_player(self.get_next_player(Game.dealer)):
                    print(" *BIG BLIND*" +'\n')
                elif i == self.get_next_player(Game.dealer):
                    print(" *SMALL BLIND*"+'\n')
                elif i == Game.dealer:
                    print(" *DEALER*"+'\n')
                else:
                    print('\n')

        print(f"POT:{self.pot}")
        print(f"Current player: {self.current_player}")
        print(f"Next player: {self.get_next_player(self.current_player)}")
        print(
        '----------------------------------------' + '\n'
        )
        if len(args) !=0:
            for i in args:
                print(f"Attention:{str(i)}")



       

Game1 = Game(players)
Round1 = Round(Game1)
'''
cards = Round.draw_cards(7)
cards_translation = set()
for i in cards:
    cards_translation.add(Round1.get_card_name(i))
print(cards_translation)
'''









     

    

        

