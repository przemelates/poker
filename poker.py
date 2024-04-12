import time, threading, copy, random, re, os
i = 0
players = ["Roe","Janus","Szynek"]
'''
print("Enter players' names:")
while(True):
     if i<9:
        player = input()
        if player == "":
             break
        players.append(player)
        i+=1
     else:
        break
'''
 
class Game:
    time = 0
    ante = 10
    small_blind = [20,0] # [value,playerId]
    big_blind = [40,1] # ditto
    dealer = 0 


    def __init__(self, players) -> None:
         self.players = set()
         for i in players:
              self.players.add(i)
         self.controlled_player = players[0]
         self.time = 0
         self.balances = dict(zip(self.players,[1000 for i in range (len(self.players))]))  # Assign 0 to every player in player list
         
    def display_time(self):
        while(True):
            time.sleep(1)
            self.time+=1
            print(self.time)
          
    def display_players(self):
         for i in self.players:
              print(i)
        


class Round(Game):

    ### Round-wide variables declaration ###
    colours = {"D": "Diamonds", "H": "Hearts", "C" : "Clubs", "S": "Spades"}
    values = {2: "Two", 3: "Three", 4:"Four", 5:"Five", 6:"Six", 7:"Seven", 8:"Eight", 9:"Nine", 10:"Ten", 11:"Jack", 12:"Queen", 13:"King", 14:"Ace"}
    round_phases = {1:"Pre-bets",2:"Flop",3:"Turn",4:"River"}
    community_cards = set()
    deck = set()
    round_phase = 1
    players = list()
    current_player = Game.dealer
    pot = 0
    player_cards = dict()
    bets = dict()
    balances = dict()

    for i in values.keys():
        for j in colours.keys():
            deck.add((i,j))        # Cards always in format tuple(value,colour)

    def __init__(self, game) -> None:
        print("Round begins...")
        Game.ante *=2
        self.players = list(game.players)
        self.balances = game.balances
        self.balances[self.players[Game.big_blind[1]]] -= Game.big_blind[0]
        self.balances[self.players[Game.small_blind[1]]] -= Game.small_blind[0]
        for i in self.players:
            self.balances[i] -= Game.ante
        self.pot = 0
        self.player_cards = dict(zip(self.players, [Round.draw_cards(2) for i in range(len(self.players))]))
        self.bets = dict(zip(self.players,[0 for i in range(len(self.players))]))
        self.bets_phases = dict(zip(list(Round.round_phases.keys()),[copy.deepcopy(self.bets) for i in range(len(Round.round_phases.keys()))]))
        self.bets[self.players[Game.small_blind[1]]] += Game.small_blind[0]
        self.bets[self.players[Game.big_blind[1]]] += Game.big_blind[0]
        self.bets_phases[1][self.players[Game.small_blind[1]]] += Game.small_blind[0]
        self.bets_phases[1][self.players[Game.big_blind[1]]] += Game.big_blind[0]
        self.next_move()
        

    ### Misc tools ###

    def get_card_name(self,cards):
        names = set()
        for i in cards:
            names.add((self.values[i[0]] + " of " + self.colours[i[1]]))
        return names
    
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
        
    def draw_cards(no):
        cards = set()
        deck_copy = copy.deepcopy(Round.deck)
        for i in range(no):
            x = random.choice(list(deck_copy))
            cards.add(x)
            deck_copy.remove(x)
       
        return cards

    ### Hand strength evaluation tools ###
    
    def check_flush(self,hand):
        for colour in self.colours.keys():
            hand1 = copy.deepcopy(hand)
            to_remove = set()
            for i in hand1:
                if i[1] != colour:
                    to_remove.add(i)
            for i in to_remove:
                hand1.remove(i)
            if len(hand1) == 5:
                top = max(hand1,key = lambda i: i[0])
                return True, top[0]
            else:
                continue
        return False
    
    def check_straight(self,hand):
        flush_array = list(hand)
        flush_array.sort(key = lambda i: i[0])  # Sort by first element
        streak = 1
        excluded = set()
        for i in range(len(flush_array)-1,0,-1):
             if(flush_array[i][0] == flush_array[i-1][0]+1):
                streak+=1
                if streak == 5:
                    for i in excluded:
                        flush_array.remove(i)
                    top = max(flush_array, key = lambda i: i[0])
                    return True, top[0]
             elif(flush_array[i][0] == flush_array[i-1][0]):
                continue
             else:
                streak = 1
                excluded.add(flush_array[i])
        return False

    
    
    def check_straight_flush(self,hand):
        if self.check_flush(hand)!= False and self.check_straight(hand)!= False:
            return True, self.check_flush(hand)[1]
        else:
            return False
           
        
    def check_royal_flush(self,hand):
        if self.check_straight_flush(hand) == False:
            return False
        else:
            royal_flush_sets = []
            for i in self.colours.keys():
                royal_flush_set = set()
                royal_flush_sets.append(royal_flush_set)
                for j in range(10,15):
                    royal_flush_set.add((j,i))
            for i in royal_flush_sets:
                if i in hand:
                    return True
            return False
        
    def check_full(self,hand):
        if self.check_pairs(hand,3)!= False and self.check_pairs(hand,2)!= False:
            return True, self.check_pairs(hand,3)[2], self.check_pairs(hand,2)[2]
        else:
            return False
        
    def check_multiples(self,hand):
        count = dict()
        for i in hand:
            if i[0] not in count.keys():
                count[i[0]] = 1
            else:
                count[i[0]] +=1
        return count
    
    def check_pairs(self,hand,size):
        max_ = max(self.check_multiples(hand).values())
        if max_ != size:
            return False
        values = list(self.check_multiples(hand).values())
        keys = list(self.check_multiples(hand).keys())
        keys.sort(reverse = True)
        for i in range(len(keys)):
            if self.check_multiples(hand)[keys[i]] == size:
                return True, values.count(max_), keys[i] # How many n-sized card multiples are in hand, what is the highest-value multiplied card
    
    
    def check_high_card(self,hand):
        flush_array = list(hand)
        flush_array.sort(key = lambda i: i[0])
        top = max(flush_array, key = lambda i: i[0])
        return top[0]

    def get_hand_value(self,hand):
        if self.check_royal_flush(hand) == True:
            print("Royal Flush")
            return 140
        elif self.check_straight_flush(hand) != False:
            print(f"Straight Flush, {self.values[self.check_straight_flush(hand)[1]]} high")
            return self.check_straight_flush(hand)[1] + 8*14
        elif self.check_pairs(hand,4)!= False:
            print(f"Four of a Kind, {self.values[self.check_pairs(hand,4)[2]]} high")
            return self.check_pairs(hand,4)[2] + 7*14
        elif self.check_full(hand)!= False:
            print(f"Full house, {self.values[self.check_full(hand)[1]]} high")
            return self.check_full(hand)[1] + 0.1*self.check_full(hand)[2] + 6*14
        elif self.check_flush(hand)!= False:
            print(f"Flush, {self.values[self.check_flush(hand)[1]]} high")
            return self.check_flush(hand)[1] + 5*14
        elif self.check_straight(hand)!= False:
            print(f"Straight, {self.values[self.check_straight(hand)[1]]} high")
            return self.check_straight(hand)[1] + 4*14
        elif self.check_pairs(hand,3)!= False:
            print(f"Three of a kind, {self.values[self.check_pairs(hand,3)[2]]} high")
            return self.check_pairs(hand,3)[2] + 3*14
        elif self.check_pairs(hand,2)!= False and self.check_pairs(hand,2)[1] == 2:
            print(f"Two pairs, {self.values[self.check_pairs(hand,2)[2]]} high")
            return self.check_pairs(hand,2)[2] + 2*14
        elif self.check_pairs(hand,2) != False:
            print(f"Pair, {self.values[self.check_pairs(hand,2)[2]]} high")
            return self.check_pairs(hand,2)[2] + 14
        else:
            print(f"{self.values[self.check_high_card(hand)]} high")
            return self.check_high_card(hand)

    
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
                for i in Round.draw_cards(3):
                    self.community_cards.add(i)
            elif self.round_phase ==3 or self.round_phase ==4:
                for i in Round.draw_cards(1):
                    self.community_cards.add(i)
            else:
                self.showdown()

        elif self.bets[self.players[self.current_player]] < max(bets):
            input1 = input("Press C to call, F to fold, X to all-in or enter the amount of your bet" + '\n')
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

    def update_balances(self,game):
        game.balances = self.balances

    def showdown(self):
        Game.big_blind[0] *=2 
        Game.small_blind[1] *=2
        Game.big_blind[1] = self.get_next_player(Game.big_blind[1])
        Game.small_blind[1] = self.get_next_player(Game.small_blind[1])

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
            if i == self.players[self.big_blind[1]]:
                print(" *BIG BLIND*" +'\n')
            elif i == self.players[self.small_blind[1]]:
                print(" *SMALL BLIND*"+'\n')
            elif i == self.players[self.dealer]:
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



       

Game1 = Game(players)
Round1 = Round(Game1)
cards = Round.draw_cards(7)
cards_translation = set()
for i in cards:
    cards_translation.add(Round1.get_card_name(i))
print(cards_translation)
print(Round1.get_hand_value(cards))









     

    

        

