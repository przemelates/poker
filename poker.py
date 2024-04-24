import time, threading, keyboard, os
from dataclasses import dataclass
from hand_evaluation import *
from card import *



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
    gametime = 0
    ante = 10
    small_blind = 20
    big_blind = 40 
    dealer: Player
    controlled_player: Player
 

    def __init__(self, players: list[Player]) -> None:
         thread1 = threading.Thread(target = Game._time)
         thread1.start()
         thread2 = threading.Thread(target = Game.exit)
         thread2.start()
         self.players = players
         for i in self.players:
            i.id = self.players.index(i)     
         Game.controlled_player = self.players[0]
         Game.dealer = self.players[0]

    def exit():
         while(True):
            if(keyboard.read_key() == 'esc'):
                os._exit(0)
         
    def _time():
        while(True):
            time.sleep(1)        
            Game.gametime +=1
        
    def display_players(self):
         for i in self.players:
              print(i)
        

class Round(Game):

    ### Round-wide variables declaration ###

    round_phases = {1:"Pre-flop",2:"Flop",3:"Turn",4:"River"}
    round_phase: int
    community_cards = set()
    deck = Deck()
    players: list[Player]
    current_player : Player
    pot = 0
    player_cards = dict()
    bets = dict()


    def __init__(self, game: Game) -> None:
        print("Round begins...")
        self.round_phase = 1
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
            cards = []
            print(f"Drawing for {i.name}")
            for x in self.deck.deal_cards(2):
                    cards.append(x)
            cards = cards[-2:]
            print(f"Drawn:{cards}")
            i.cards = cards
        
        self.bets = dict(zip(self.players,[0 for i in range(len(self.players))]))
        self.bets[small_blind] += Game.small_blind
        self.bets[big_blind] += Game.big_blind
        self.next_move()
        

    ### Misc tools ###
    
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
    
          
    ### Round course and administration ###

    def next_player(self):
            self.current_player = self.get_next_player(self.current_player)
      

    def next_move(self, *args):
        self.Interface(args)
        bets = list(self.bets.values())
        if (False not in [bets[i] == bets[i+1] for i in range(0,len(bets)-1)]) and (0 not in bets) and (False not in [p.has_acted[self.round_phase] for p in self.players]): 
            self.round_phase +=1
            print("Moving onto the next round phase...")
            if self.round_phase == 2:
                print("Flop")
                for i in self.deck.deal_cards(3):
                    self.community_cards.add(i)
                self.next_move()
            elif self.round_phase == 3 or self.round_phase ==4:
                print("Turn/River")
                for i in self.deck.deal_cards(1):
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
            elif False not in [i in [str(j) for j in range(10)] for i in input1]:
                self.bet(self.current_player, int(input1))
            else:
                self.next_move("Inadmissible action")


        
        else:
            input1 = input("Press C to check, X to all-in or enter the amount of your bet"+ '\n')
            if input1 == "C":
                self.check(self.current_player)
            elif input1 == "X":
                self.bet(self.current_player, self.current_player.balance)
            elif False not in [i in [str(j) for j in range(10)] for i in input1]:
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
        if ([i.has_folded for i in self.players].count(False)) == 1:
            os._exit(0)
        else:
            self.next_player()
            self.next_move(f"{player} has folded")

    def showdown(self):
        print("Showdown")
        Game.big_blind *=2 
        Game.small_blind *=2
        Game.dealer = self.get_next_player(Game.dealer)
        os._exit(0)

    ##############################################
    
    def Interface(self, *args):
        print( '\n' +
        '----------------------------------------' + '\n'
        + "SKAWINA HOLD'EM" + '\n' 
        )
        print(f"Time elapsed: {SUITS_COLOR['♥']}{Game.gametime}\033[39m")
        print(f"Your cards: {[(i.name, i.cards) for i in self.players]}" )
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
        if len(args) !=0:
            for i in args:
                print(f"Attention:{str(i)}")
        print(
        '----------------------------------------' + '\n'
        )
        
        

Game1 = Game(players)
Round1 = Round(Game1)















     

    

        

