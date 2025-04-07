from app.models.card import Card
from app.models.deck import StandartDeck, Deck

deck = StandartDeck()

class Player:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance
        self.hand = []  # Список объектов Card
        self.is_all_in = False
        self.all_in_amount = 0
        self.current_bet = 0
        self.folded = False
        
    def bet(self, amount):
        """Метод для ставки игрока."""
        if amount > self.balance:
            raise ValueError(f"{self.name} не может поставить больше, чем у него на балансе.")
        self.balance -= amount
        if self.balance == 0:
            self.is_all_in = True  # Если баланс стал 0, то игрок идет all-in
            self.all_in_amount = amount  # Сохраняем сумму ставки
        print(f"{self.name} поставил {amount}. Баланс: {self.balance}")   

    def receive_card(self, card):
        """ Добавляет карту в руку игрока. """
        self.hand.append(card)

    def show_hand(self):
        """ Открывает карты игрока. """
        for card in self.hand:
            card.reveal()

    def fold_hand(self):
        """ Фолдим руку, скрывая карты. """
        for card in self.hand:
            card.hide()
        self.is_all_in = False
        self.all_in_amount = 0
        self.hand.clear()
    
    def can_bet(self, amount):
        return self.balance > amount
    
    def card_count(self):
        return len(self.cards)
    
    def replace_card(self, indexes, deck):
        
        indexes = list(map(int, input("Enter indexes of cards to replace: ").split()))
        for i in sorted(indexes, reverse=True):  
            self.hand.pop(i)  # Удаляем по индексу
            self.hand.append(deck.draw_card())
    
    def player_interface(self, player):
        
        while True:
            action = input(f"{player.name}, выберите действие: [show_hand, replace_card]: ").strip().lower()
            
            actions = {
                "show_hand": self.show_hand,
                "replace_card": self.replace_card
            }
            
            if action in actions:
                actions[action](player)
                break  # Выход из цикла при корректном вводе
            else:
                print("Некорректное действие! Попробуйте снова.")

            
                
            
    
    
