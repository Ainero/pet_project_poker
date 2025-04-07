
def extract_values(cards):
    rank_map = {
        "Two": 2, "Three": 3, "Four": 4, "Five": 5, "Six": 6, "Seven": 7,
        "Eight": 8, "Nine": 9, "Ten": 10, "Jack": 11, "Queen": 12, "King": 13, "Ace": 14
    }

    ranks = [rank_map[card.rank] for card in cards]  # Преобразуем строки в числа
    suits = [card.suit for card in cards]
    
    return ranks, suits
