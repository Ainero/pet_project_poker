import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import random
from app.models.deck import Deck, StandartDeck
from app.models.player import Player

class Dealer:
    def __init__(self, deck=None):
        """Инициализация дилера с возможностью передачи кастомной колоды."""
        self.deck = deck or StandartDeck()  # Позволяет передавать другую колоду при необходимости
        self.community_cards = []
        self.round_counter = 0

    def shuffle_deck(self):
        """Перемешивает колоду."""
        self.deck.shuffle()

    def deal_hole_cards(self, players):
        """Раздаёт игрокам по две карманные карты."""
        for player in players:
            player.hand = [self.deck.draw_card() for _ in range(2)]

    def deal_community_cards(self, stage):
        """Раздаёт карты на стол в зависимости от этапа игры."""
        cards_to_deal = 3 if stage == "flop" else 1  # 3 карты на флоп, 1 на остальных этапах
        self.community_cards.extend(self.deck.draw_card() for _ in range(cards_to_deal))
        self.round_counter += 1

    def reset_round(self):
        """Сбрасывает стол и создаёт новую колоду."""
        self.community_cards.clear()  # Очищаем общие карты
        self.deck = StandartDeck()
        self.shuffle_deck()
        
