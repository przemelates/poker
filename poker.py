import time, threading, keyboard, os
from dataclasses import dataclass
from hand_evaluation import *
from card import *
from poker_AI import*

@dataclass
class Player:
    name: str
    id: int = 0
    has_folded: bool = False
    cards = list() 
    balance: int = 1000
    has_acted  =  dict({p: False for p in range(1,5)})
    position : int = 0 
    positions = {9:"Big blind",8:"Small blind", 7:"Dealer", 6: "CO", 5:"MP", 4:"UTG", 3:"UTG-1", 2:"UTG-2", 1:"UTG-3"}

    def __hash__(self) -> int:
        return self.name.__hash__()
    def __str__(self) -> str:
        return self.name
    
    def reset(self):
        self.has_folded = False
        self.has_acted = {p: False for p in range(1,5)}

    def cycle_position(self):
        if self.position +1 > 9:
            self.position = 10-len(players)
        else:
            self.position +=1

    def check_allin(self):
        if self.balance == 0:
            self.has_acted = dict({p: True for p in range(1,5)})
            return f"{SUITS_COLOR['♥']}ALL IN\033[39m"
        else:
            return ""

players = [Player("Roe", position= 7 ),Player("Janus", position= 8),Player("Szynek", position= 9)]
for i in players:
    i.reset()

class Game:
    time_0 : float
    ante = 10
    small_blind = 20
    big_blind = 40 
    dealer: Player
    controlled_player: Player
 

    def __init__(self, players: list[Player]) -> None:
         self.time_0 = time.time()
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
    big_blind_player : Player 
    pot = 0
    player_cards = dict()
    bets = dict()


    def __init__(self, game: Game) -> None:
        print("Round begins...")
        self.community_cards = set()
        self.game = game
        self.round_phase = 1
        Game.ante *=2
        self.pot = Game.big_blind + Game.small_blind
        self.players: list[Player] = game.players
        self.bets = dict(zip(self.players,[0 for i in range(len(self.players))]))

        for i in self.players:
            i.balance -= Game.ante
            if(i.position == 10-len(players)):
                self.current_player = i
            if(i.position == 8):
                i.balance -= Game.small_blind
                self.bets[i] += Game.small_blind
            elif(i.position == 9):
                i.balance -=Game.big_blind
                self.bets[i] +=Game.big_blind
                self.big_blind_player = i
            else:
                continue
        
        for i in self.players:
            cards = []
            print(f"Drawing for {i.name}")
            for x in self.deck.deal_cards(2):
                    cards.append(x)
            cards = cards[-2:]
            print(f"Drawn:{cards}")
            i.cards = cards

        self.next_move()
        
    ### Getters ###
    
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
     
    def get_actions(self, player : Player):
        if player.has_folded == True:
           return None
        else:
           actions = dict()
           if self.bets[player] < self.get_max_bet():
               actions['C'] = "self.call(self.current_player, self.get_max_bet() - self.bets[self.current_player])" 
               actions['F'] = "self.fold(self.current_player)" 
               actions['B'] = "self.bet(self.current_player, random.randint(self.get_max_bet()-self.bets[self.current_player],self.current_player.balance))" 
           else:
               actions['C'] = "self.check(self.current_player)" 
               actions['B'] = "self.bet(self.current_player, random.randint(self.get_max_bet()-self.bets[self.current_player],self.current_player.balance))"
        return actions

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
                self.current_player = self.get_next_player(self.big_blind_player)
                self.next_move()
            elif self.round_phase == 3 or self.round_phase ==4:
                print("Turn/River")
                for i in self.deck.deal_cards(1):
                    self.community_cards.add(i)
                self.current_player = self.get_next_player(self.big_blind_player)
                self.next_move()
            else:
                self.showdown()

        elif self.bets[self.current_player] < self.get_max_bet():
            if(self.current_player == self.game.controlled_player):
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
            elif self.current_player != self.controlled_player and self.round_phase == 1:
                actions = self.get_actions(self.current_player)
                flag = True
                for player in players:
                    if player.position < self.current_player.position and player.has_folded == False:
                        flag = False
                        break
                    else:
                        continue
                choice = charts(self.current_player.cards,self.current_player.position-10+len(self.players))
                x = exec(actions[choice])
            else:
                actions = self.get_actions(self.current_player)
                choice = random_action(actions)
                x = exec(actions[choice])
                


        
        else:
            if(self.current_player == self.game.controlled_player):
                input1 = input("Press C to check, X to all-in or enter the amount of your bet"+ '\n')
                if input1 == "C":
                    self.check(self.current_player)
                elif input1 == "X":
                    self.bet(self.current_player, self.current_player.balance)
                elif False not in [i in [str(j) for j in range(10)] for i in input1]:
                    self.bet(self.current_player, int(input1))
                else:
                    self.next_move("Inadmissible action")
            else:
                actions = self.get_actions(self.current_player)
                choice = random_action(actions)
                x = exec(actions[choice])
               


    def bet(self,player: Player,amount):
        if player.balance >=amount and amount+self.bets[player] >= self.get_max_bet():
            player.balance -= amount
            self.bets[player] +=amount
            self.pot += amount
            player.has_acted[self.round_phase] = True
            player.check_allin()
            self.next_player()
            self.next_move(f"{player} bets {amount}")
        else:
            self.next_move("Inadmissible bet size")
    
    call = bet

    def check(self,player:Player):
        player.has_acted[self.round_phase] = True
        self.next_player()
        self.next_move(f"{player} checks")

    def fold(self,player:Player):
        for i in self.round_phases.keys():
            player.has_acted[i] = True
        player.has_folded = True
        del self.bets[player] 
        if ([i.has_folded for i in self.players].count(False)) == 1:
            self.showdown()
        else:
            self.next_player()
            self.next_move(f"{player} folds")

    def showdown(self):
        print(f"{SUITS_COLOR['♥']}Showdown\n\033[39m")
        Game.big_blind *=2 
        Game.small_blind *=2
        Game.dealer = self.get_next_player(Game.dealer)
        hands_values = dict(zip(self.players,[0 for i in range(len(self.players))]))
        for i in self.players:
            if i.has_folded == False:
                hand = i.cards + list(self.community_cards)
                print(f"{i}:", end="")
                x = HandEvaluator.get_hand_value(hand)
                hands_values[i] = x
        self.pot = self.pot/(list(hands_values.values()).count(max(hands_values.values())))
        for i in self.players:
            if hands_values[i] == max(hands_values.values()):
                i.balance += round(self.pot)
                print(f"\n{i} wins the pot: {self.pot}")
        
        players_copy = copy.deepcopy(self.players)
        for i in self.players:
            if i.balance <= 0:
                players_copy.remove(i)
                print(f"{i} busts out!")

        players = players_copy

        if len(players) == 1:
            print(f"\033[96m{players[0]} wins the game, cheers\033[39m")
            os._exit(0)

        def play_next(self):
            print("Play next round?\nY/N")
            input1 = input()
            if input1 == "Y":
                for i in players:
                    i.reset()
                    i.cycle_position()
                Game_n = Game(players)
                Round_n = Round(Game_n)
            elif input1 == "N":
                os._exit(0)
            else:
                play_next(self)
        play_next(self)


    ##############################################
    
    def Interface(self, *args):
        print( '\n' +
        '----------------------------------------' + '\n'
        + "SKAWINA HOLD'EM" + '\n' 
        )
        print(f"Time elapsed: {SUITS_COLOR['♥']}{round(time.time() - self.game.time_0,2)}\033[39m")
        print(f"Your cards: {[(i.name, i.cards) for i in self.players]}" )
        print(f"Community cards: {self.community_cards}"+'\n')
        for i in self.players:
            if(i.has_folded == False):
                print(f"{i}: {i.balance}, bets {self.bets[i]} {i.check_allin()}")
                if i.position == 9:
                    print(" *BIG BLIND*" +'\n')
                elif i.position == 8:
                    print(" *SMALL BLIND*"+'\n')
                elif i.position == 7:
                    print(" *DEALER*"+'\n')
                else:
                    print('\n')
            else:
                print(f"{i}: {i.balance} FOLDED")
                if i.position == 9:
                    print(" *BIG BLIND*" +'\n')
                elif i.position == 8:
                    print(" *SMALL BLIND*"+'\n')
                elif i.position == 7:
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















     

    

        

