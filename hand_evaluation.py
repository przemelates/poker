import copy
class HandEvaluator():
     
     colours = {"D": "♦", "H": "♣", "C": "♣", "S": "♠"}
     values = {2: "Two", 3: "Three", 4:"Four", 5:"Five", 6:"Six", 7:"Seven", 8:"Eight", 9:"Nine", 10:"Ten", 11:"Jack", 12:"Queen", 13:"King", 14:"Ace"}
     
     ##Hand strength evaluation tools
     @staticmethod
     def check_flush(hand):
        for colour in HandEvaluator.colours.keys():
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
     
     @staticmethod
     def check_straight(hand):
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

    
     @staticmethod
     def check_straight_flush(hand):
        if HandEvaluator.check_flush(hand)!= False and HandEvaluator.check_straight(hand)!= False:
            return True, HandEvaluator.check_flush(hand)[1]
        else:
            return False
           
     @staticmethod   
     def check_royal_flush(hand):
        if HandEvaluator.check_straight_flush(hand) == False:
            return False
        else:
            royal_flush_sets = []
            for i in HandEvaluator.colours.keys():
                royal_flush_set = set()
                royal_flush_sets.append(royal_flush_set)
                for j in range(10,15):
                    royal_flush_set.add((j,i))
            for i in royal_flush_sets:
                if i in hand:
                    return True
            return False
        
     @staticmethod   
     def check_full(hand):
        if HandEvaluator.check_pairs(hand,3)!= False and HandEvaluator.check_pairs(hand,2)!= False:
            return True, HandEvaluator.check_pairs(hand,3)[2], HandEvaluator.check_pairs(hand,2)[2]
        else:
            return False
        
     @staticmethod   
     def check_multiples(hand) -> dict :
        count = dict()
        for i in hand:
            if i[0] not in count.keys():
                count[i[0]] = 1
            else:
                count[i[0]] +=1
        return count
     
     @staticmethod
     def check_pairs(hand,size):
        max_ = max(HandEvaluator.check_multiples(hand).values())
        if max_ != size:
            return False
        values = list(HandEvaluator.check_multiples(hand).values())
        keys = list(HandEvaluator.check_multiples(hand).keys())
        keys.sort(reverse = True)
        for i in range(len(keys)):
            if HandEvaluator.check_multiples(hand)[keys[i]] == size:
                return True, values.count(max_), keys[i] # How many n-sized card multiples are in hand, what is the highest-value multiplied card
    
     @staticmethod
     def check_high_card(hand):
        flush_array = list(hand)
        flush_array.sort(key = lambda i: i[0])
        top = max(flush_array, key = lambda i: i[0])
        return top[0]
     
     @staticmethod
     def get_hand_value(hand):
        if HandEvaluator.check_royal_flush(hand) == True:
            print("Royal Flush")
            return 140
        elif HandEvaluator.check_straight_flush(hand) != False:
            print(f"Straight Flush, {HandEvaluator.values[HandEvaluator.check_straight_flush(hand)[1]]} high")
            return HandEvaluator.check_straight_flush(hand)[1] + 8*14
        elif HandEvaluator.check_pairs(hand,4)!= False:
            print(f"Four of a Kind, {HandEvaluator.values[HandEvaluator.check_pairs(hand,4)[2]]} high")
            return HandEvaluator.check_pairs(hand,4)[2] + 7*14
        elif HandEvaluator.check_full(hand)!= False:
            print(f"Full house, {HandEvaluator.values[HandEvaluator.check_full(hand)[1]]} high")
            return HandEvaluator.check_full(hand)[1] + 0.1*HandEvaluator.check_full(hand)[2] + 6*14
        elif HandEvaluator.check_flush(hand)!= False:
            print(f"Flush, {HandEvaluator.values[HandEvaluator.check_flush(hand)[1]]} high")
            return HandEvaluator.check_flush(hand)[1] + 5*14
        elif HandEvaluator.check_straight(hand)!= False:
            print(f"Straight, {HandEvaluator.values[HandEvaluator.check_straight(hand)[1]]} high")
            return HandEvaluator.check_straight(hand)[1] + 4*14
        elif HandEvaluator.check_pairs(hand,3)!= False:
            print(f"Three of a kind, {HandEvaluator.values[HandEvaluator.check_pairs(hand,3)[2]]} high")
            return HandEvaluator.check_pairs(hand,3)[2] + 3*14
        elif HandEvaluator.check_pairs(hand,2)!= False and HandEvaluator.check_pairs(hand,2)[1] == 2:
            print(f"Two pairs, {HandEvaluator.values[HandEvaluator.check_pairs(hand,2)[2]]} high")
            return HandEvaluator.check_pairs(hand,2)[2] + 2*14
        elif HandEvaluator.check_pairs(hand,2) != False:
            print(f"Pair, {HandEvaluator.values[HandEvaluator.check_pairs(hand,2)[2]]} high")
            return HandEvaluator.check_pairs(hand,2)[2] + 14
        else:
            print(f"{HandEvaluator.values[HandEvaluator.check_high_card(hand)]} high")
            return HandEvaluator.check_high_card(hand)