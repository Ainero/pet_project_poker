class Card:
    suits = {"Hearts": "♡", "Spades": "♠", "Diamonds": "♢", "Clubs": "♣"}
    ranks = {
        "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7,
        "Eight": 8, "Nine": 9, "Ten": 10, "Jack": 11, "Queen": 12, "King": 13, "Ace": 14
    }

    def __init__(self, suit: str, rank: str):
        if suit not in self.suits:
            raise ValueError(f"Invalid card suit: {suit}")
        if rank not in self.ranks:
            raise ValueError(f"Invalid card rank: {rank}")

        self.suit = suit
        self.rank = rank
        self.symbol = self.generate_symbol()
        self.showing = False

    def generate_symbol(self):
        """ Создает строковое представление карты с символами масти. """
        suit_icon = self.suits[self.suit]
        value = self.ranks[self.rank]

        if value < 11:
            return f"{value}{suit_icon}"
        else:
            return f"{self.rank[0]}{suit_icon}"  # J, Q, K, A первой буквой

    def __repr__(self):
        return self.symbol if self.showing else "Card"

    def __str__(self):
        return f"{self.rank} of {self.suit}"

    def reveal(self):
        """ Открывает карту (делает её видимой). """
        self.showing = True

    def hide(self):
        """ Скрывает карту (делает её невидимой). """
        self.showing = False
