from app.models.card import Card
import random

class Deck:
    def shuffle(self):
        random.shuffle(self.cards)
        print('Deck Shuffled')
        
    def deal(self):
        return self.cards.pop(0)


class StandartDeck(Deck):
    
    def __init__(self):
        self.cards = [Card(suit, rank) for suit in Card.suits for rank in Card.ranks]

        
    def create_deck(cls):
        return [Card(suit, rank) for suit in Card.suits for rank in Card.ranks]
    
    def shuffle_deck(self):
        random.shuffle(self.cards)
        
    def draw_card(self):
        """Выдает карту из колоды."""
        if self.cards:
            
            return self.cards.pop() if self.cards else None
        else:
            print("Недостаточно карт")
            return None