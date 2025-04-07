import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.models.player import Player
from collections import Counter
from utils.poker_utils import extract_values
from itertools import combinations
from utils.error_handler import log_error, log_info
from app.models.card import Card

import traceback

class HandEvaluator:
    
    def __init__(self, community_cards):
        self.community_cards = community_cards

    def best_hand(self, player):
        all_cards = player.hand + self.community_cards
        best_rank, best_combo = max(
            (self.evaluate_hand(combo), combo) for combo in combinations(all_cards, 5)
        )
        return best_rank, best_combo 
    
    @staticmethod
    def compare_hands(hand1, hand2):
        """Сравнивает две руки с одинаковыми комбинациями."""
        
        r1 = Card.ranks[hand1[0].rank]  # Получаем числовой ранг
        r2 = Card.ranks[hand2[0].rank]

        for c1, c2 in zip(hand1, hand2):
            rank1 = Card.ranks[c1.rank]
            rank2 = Card.ranks[c2.rank]
            if rank1 > rank2:
                return 1
            elif rank1 < rank2:
                return -1
        return 0  # Полная ничья

    def is_flush(self, suits):
        return len(set(suits)) == 1
        
    def is_straight(self, ranks):
        unique_ranks = sorted(set(ranks), reverse=True)
        return any(unique_ranks[i] - unique_ranks[i + 4] == 4 for i in range(len(unique_ranks) - 4))
        
    def get_rank_counts(self, ranks):
        return Counter(ranks)
                    
    def evaluate_hand(self, cards):
        ranks, suits = extract_values(cards)
        flush = self.is_flush(suits)
        straight = self.is_straight(ranks)
        rank_counts = self.get_rank_counts(ranks)
        
        sorted_ranks = sorted(ranks, reverse=True)  # Сортируем один раз

        if flush and straight:
            return (9 if sorted_ranks == [14, 13, 12, 11, 10] else 8, sorted_ranks)

        if 4 in rank_counts.values():
            return (7, sorted_ranks, rank_counts)

        if sorted(rank_counts.values()) == [2, 3]:
            return (6, sorted_ranks, rank_counts)

        if flush:
            return (5, sorted_ranks)

        if straight:
            return (4, sorted_ranks)

        if 3 in rank_counts.values():
            return (3, sorted_ranks, rank_counts)

        if list(rank_counts.values()).count(2) == 2:
            return (2, sorted_ranks, rank_counts)

        if 2 in rank_counts.values():
            return (1, sorted_ranks, rank_counts)

        return (0, sorted_ranks)


    def determine_winners(self, players):
        try:
            if not players:
                log_error(ValueError("No players to determine the winner."), "Error in determining winners")
                return []

            best_rank = -1
            winners = []

            for player in players:
                hand_rank, best_hand = self.best_hand(player)
                if hand_rank[0] > best_rank:
                    best_rank = hand_rank[0]
                    winners = [(player, best_hand)]
                elif hand_rank[0] == best_rank:
                    comparison = self.compare_hands(best_hand, winners[0][1])
                    if comparison > 0:
                        winners = [(player, best_hand)]
                    elif comparison == 0:
                        winners.append((player, best_hand))
                        
            return [winner[0] for winner in winners]
        except Exception as e:
            log_error(e, "Error in determining winners.")
            print("An error occurred while determining the winners.")
            print(traceback.format_exc())
            