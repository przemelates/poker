import copy
import card
class HandEvaluator:
     
     
     ##Hand strength evaluation tools
     @staticmethod
     def check_flush(hand : list[card.Card]):
        for colour in card.COLOURS.keys():
            hand1 = copy.deepcopy(hand)
            to_remove = set()
            for i in hand1:
                if i.suit != colour:
                    to_remove.add(i)
            for i in to_remove:
                hand1.remove(i)
            if len(hand1) == 5:
                top = max(hand1,key = lambda i: i.value)
                return True, top.value
            else:
                continue
        return False
     
     @staticmethod
     def check_straight(hand : list[card.Card]):
        flush_array = list(hand)
        flush_array.sort(key = lambda i: i.value)  # Sort by first element
        streak = 1
        excluded = set()
        for i in range(len(flush_array)-1,0,-1):
             if(flush_array[i].value == flush_array[i-1].value+1):
                streak+=1
                if streak == 5:
                    for i in excluded:
                        flush_array.remove(i)
                    top = max(flush_array, key = lambda i: i.value)
                    return True, top.value
             elif(flush_array[i].value == flush_array[i-1].value):
                continue
             else:
                streak = 1
                excluded.add(flush_array[i])
        return False

    
     @staticmethod
     def check_straight_flush(hand : list[card.Card]):
        if HandEvaluator.check_flush(hand)!= False and HandEvaluator.check_straight(hand)!= False:
            return True, HandEvaluator.check_flush(hand)[1]
        else:
            return False
           
     @staticmethod   
     def check_royal_flush(hand: list[card.Card]):
        if HandEvaluator.check_straight_flush(hand) == False:
            return False
        else:
            royal_flush_sets = []
            for i in card.COLOURS.keys():
                royal_flush_set = set()
                royal_flush_sets.append(royal_flush_set)
                for j in range(10,15):
                    royal_flush_set.add(card.Card(i,j))
            for i in royal_flush_sets:
                if i in hand:
                    return True
            return False
        
     @staticmethod   
     def check_full(hand : list[card.Card]):
        if HandEvaluator.check_pairs(hand,3)!= False and HandEvaluator.check_pairs(hand,2)!= False:
            return True, HandEvaluator.check_pairs(hand,3)[2], HandEvaluator.check_pairs(hand,2)[2]
        else:
            return False
        
     @staticmethod   
     def check_multiples(hand: list[card.Card]) -> dict :
        count = dict()
        for i in hand:
            if i.value not in count.keys():
                count[i.value] = 1
            else:
                count[i.value] +=1
        return count
     
     @staticmethod
     def check_pairs(hand: list[card.Card],size):
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
     def check_high_card(hand: list[card.Card]):
        flush_array = list(hand)
        flush_array.sort(key = lambda i: i.value)
        top = max(flush_array, key = lambda i: i.value)
        return top.value
     
     @staticmethod
     def get_hand_value(hand: list[card.Card]):
        if HandEvaluator.check_royal_flush(hand) == True:
            print("Royal Flush")
            return 140
        elif HandEvaluator.check_straight_flush(hand) != False:
            print(f"Straight Flush, {card.VALUES[HandEvaluator.check_straight_flush(hand)[1]]} high")
            return HandEvaluator.check_straight_flush(hand)[1] + 8*14
        elif HandEvaluator.check_pairs(hand,4)!= False:
            print(f"Four of a Kind, {card.VALUES[HandEvaluator.check_pairs(hand,4)[2]]} high")
            return HandEvaluator.check_pairs(hand,4)[2] + 7*14
        elif HandEvaluator.check_full(hand)!= False:
            print(f"Full house, {card.VALUES[HandEvaluator.check_full(hand)[1]]} high")
            return HandEvaluator.check_full(hand)[1] + 0.1*HandEvaluator.check_full(hand)[2] + 6*14
        elif HandEvaluator.check_flush(hand)!= False:
            print(f"Flush, {card.VALUES[HandEvaluator.check_flush(hand)[1]]} high")
            return HandEvaluator.check_flush(hand)[1] + 5*14
        elif HandEvaluator.check_straight(hand)!= False:
            print(f"Straight, {card.VALUES[HandEvaluator.check_straight(hand)[1]]} high")
            return HandEvaluator.check_straight(hand)[1] + 4*14
        elif HandEvaluator.check_pairs(hand,3)!= False:
            print(f"Three of a kind, {card.VALUES[HandEvaluator.check_pairs(hand,3)[2]]} high")
            return HandEvaluator.check_pairs(hand,3)[2] + 3*14
        elif HandEvaluator.check_pairs(hand,2)!= False and HandEvaluator.check_pairs(hand,2)[1] == 2:
            print(f"Two pairs, {card.VALUES[HandEvaluator.check_pairs(hand,2)[2]]} high")
            return HandEvaluator.check_pairs(hand,2)[2] + 2*14
        elif HandEvaluator.check_pairs(hand,2) != False:
            print(f"Pair, {card.VALUES[HandEvaluator.check_pairs(hand,2)[2]]} high")
            return HandEvaluator.check_pairs(hand,2)[2] + 14
        else:
            print(f"{card.VALUES[HandEvaluator.check_high_card(hand)]} high")
            return HandEvaluator.check_high_card(hand)