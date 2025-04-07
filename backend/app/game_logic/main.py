import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import logging
import traceback
from app.models.player import Player
from app.game_logic.dealing_cards import Dealer
from app.game_logic.betting import *
from app.game_logic.hand_evaluator import HandEvaluator
from utils.error_handler import log_error, log_info  # Импорт логирования ошибок

logging.basicConfig(
    filename='game_log.log',
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

print("Starting Poker Game...")

class PokerGame:
    def __init__(self):
        self.players = []
        self.dealer = Dealer()
        #self.player = Player()
        self.betting = BettingRound(self.players, self.dealer)
        self.hand_evaluator = HandEvaluator([])# Сообщи, если требуется передавать карты
        log_info("Poker game initialized")

    def initialize_players(self):
        """Инициализация игроков."""
        print("Initializing players...")
        try:
            num_players = int(input("Enter number of players: "))
            for _ in range(num_players):
                name = input("Enter player's name: ")
                balance = int(input(f"Enter {name}'s starting balance: "))
                self.players.append(Player(name, balance))
            log_info(f"{num_players} players initialized")
        except Exception as e:
            log_error(e, "Error initializing players")

    def start_round(self):
        """Запуск раунда игры."""
        try:
            self.dealer.shuffle_deck()
            self.dealer.deal_hole_cards(self.players)
            self.dealer.deal_community_cards("flop")
            self.betting.place_bets()

            self.dealer.deal_community_cards("turn")
            self.betting.start_new_round()

            self.dealer.deal_community_cards("river")
            self.betting.start_new_round()
            

            self.evaluate_hands()
            log_info("Round completed successfully")
        except Exception as e:
            log_error(e, "Error starting round")


    def evaluate_hands(self):
        """Оценка рук игроков."""
        try:
            self.hand_evaluator.community_cards = self.dealer.community_cards
            for player in self.players:
                best_rank, best_hand = self.hand_evaluator.best_hand(player)
                log_info(f"{player.name}'s best hand: {best_hand}")
            log_info("Hands evaluated successfully")
        except Exception as e:
            log_error(e, "Error evaluating hands")

    def play(self):
        """Основной цикл игры."""
        print("Starting the game...")
        try:
            self.initialize_players()

            while True:
                self.start_round()
                winner = self.evaluate_hands()
                
                # Определяем победителя текущей раздачи
                winners = self.hand_evaluator.determine_winners(self.players)

                if winners:
                    if len(winners) == 1:
                        print(f"{self.hand_evaluator.best_combo}")
                        print(f"Победитель раздачи: {winners[0].name}!")
                    else:
                        print("Ничья между:", ", ".join(w.name for w in winners))
                else:
                    print("Победителей нет!")
                    
                self.distribute_pot(winners)  # Раздача выигрыша
                

                # Проверяем, остались ли игроки с фишками
                remaining_players = [p for p in self.players if p.balance > 0]
                if len(remaining_players) < 2:
                    print(f"Game over! Winner: {remaining_players[0].name}" if remaining_players else "No winners!")
                    break

                # Сброс состояния игроков
                self.reset_players()

                another_round = input("Play another round? (y/n): ")
                if another_round.lower() != 'y':
                    break


            log_info("Game ended successfully")
        
        except Exception as e:
            log_error(e, "Error during game play")


if __name__ == "__main__":
    print("Initializing game...")
    try:
        game = PokerGame()
        print("Game initialized.")
        game.play()
    except Exception as e:
        log_error(e, "Critical error in main game loop")
