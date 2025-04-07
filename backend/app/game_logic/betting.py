import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app.game_logic.hand_evaluator import HandEvaluator
from app.game_logic.dealing_cards import Dealer
from utils.error_handler import log_error, log_info
from app.models.deck import StandartDeck
from app.models.card import Card
from app.models.player import Player


class PotManager:

    def __init__(self):
        self._pot = 0

    @property
    def pot(self):
        return self._pot

    @pot.setter
    def pot(self, amount):
        if amount < 0:
            raise ValueError("Сумма не может быть отрицательной!")
        self._pot += amount

    def split_pot(self, pot, winners):

        if not winners:
            return 0

        share = pot//len(winners)
        remainder = pot % len(winners)

        for winner in winners:
            winner.balance += share

        winners[0].balance += remainder
        return pot


class PlayerActionHandler:

    def __init__(self, betting_round):
        self.betting_round = betting_round

    def handle_fold(self, player):

        player.fold_hand()
        player.folded = True
        print(f"{player.name} сбросил карты!")

    def handle_call(self, player):
        try:
            # Рассчитываем сумму для колла как разницу между текущей ставкой и ставкой игрока
            amount = self.betting_round.current_bet - player.current_bet

            # Если сумма колла меньше или равна нулю, это может означать, что ставка уже была выполнена
            if amount <= 0:
                print(f"{player.name} has already matched the current bet.")
                return

            # Проверяем, есть ли у игрока достаточно средств для колла
            if not player.can_bet(amount):
                log_error(ValueError(f"{player.name} does not have enough balance for this call."),
                        f"Error while processing call for player {player.name}.")
                print(f"{player.name} does not have enough balance to call.")
                return

            # Игрок делает ставку
            player.bet(amount)
            self.betting_round.pot_manager.pot += amount
            print(f"{player.name} called with {amount}!")

        except Exception as e:
            log_error(e, f"Error in handling call for player {player.name}.")
            print("An error occurred while processing the call.")





    def handle_raise(self, player):
        try:
            while True:
                try:
                    amount = int(input(f"{player.name}, enter raise amount: "))
                    min_raise = self.betting_round.current_bet * 2
                    if amount < min_raise:
                        print(f"Raise must be at least {min_raise}.")
                        continue
                    if not player.can_bet(amount):
                        print(f"{player.name} does not have enough balance for this raise.")
                        continue
                    break
                except ValueError as e:
                    log_error(e, f"Invalid input for raise amount from player {player.name}.")
                    print("Invalid input. Please enter a number.")

            self.betting_round.current_bet = amount
            player.bet(amount)
            self.betting_round.pot_manager.pot += amount
            print(f"{player.name} raised to {amount}!")
        except Exception as e:
            log_error(e, f"Error in handling raise for player {player.name}.")
            print("An error occurred while processing the raise.")

    def handle_all_in(self, player):

        amount = player.balance
        player.is_all_in = True
        player.all_in_amount = amount
        self.betting_round.current_bet = max(
            self.betting_round.current_bet, amount)
        player.bet(amount)
        self.betting_round.pot_manager.pot += amount
        print(f"{player.name} поставил все на кон! Баланс: {player.balance}")

        return self.calculate_side_pots()

    def calculate_side_pots(self):

        all_in_players = sorted(
            [p for p in self.betting_round.players if p.is_all_in], key=lambda x: x.all_in_amount)
        side_pots = []
        last_amount = 0

        for i, p in enumerate(all_in_players):
            side_pot_amount = (p.all_in_amount - last_amount) * \
                (len(self.betting_round.players) - i)
            side_pots.append(side_pot_amount)
            last_amount = p.all_in_amount

        return side_pots


class BettingRound:

    def __init__(self, players, dealer):
        self.players = players
        self.pot_manager = PotManager()
        self.action_handler = PlayerActionHandler(self)
        self.dealer = dealer
        self._current_bet = 0
        self.current_player = None

    @property
    def current_bet(self):
        return self._current_bet

    @current_bet.setter
    def current_bet(self, amount):
        if amount < 0:
            raise ValueError("Ставка не может быть отрицательной!")
        self._current_bet = amount

    def next_player(self):
        if self.players:
            self.current_player = self.players.pop(0)
            self.players.append(self.current_player)

    def place_bets(self):
        round_active = True
        while round_active:
            for player in self.players:
                if player.folded or (player.balance == 0 and player.current_bet == self.current_bet):
                    continue  # Пропускаем игроков, которые сбросили карты или уже на максимальной ставке

                self.current_player = player
                print(f"Игрок: {player.name}, баланс: {player.balance}, текущая ставка: {self.current_bet}")
                print(f"Твои карты: {', '.join(str(card) for card in player.hand)}")
                print(f"Карты на столе: {', '.join(str(card) for card in self.dealer.community_cards)}")

                while True: 
                    action = input(f"{player.name}, выберите действие: [call, raise, fold, all_in]: ").strip().lower()

                    actions = {
                        "fold": self.action_handler.handle_fold,
                        "call": self.action_handler.handle_call,
                        "raise": self.action_handler.handle_raise,
                        "all_in": self.action_handler.handle_all_in,
                    }

                    if action in actions:
                        actions[action](player)
                        break  # Выход из цикла выбора действия
                    else:
                        print("Некорректное действие! Попробуйте снова.")
                        
            side_pots = self.action_handler.calculate_side_pots()
            self.distributive_winnings(winners, side_pots)
            
            # Если все игроки в all-in или сбросили карты
            if all(p.is_all_in or p.folded for p in self.players):
                print("Все ставки сделаны!")
                
                # Определяем победителя
                winners = self.determine_winners()  

                # Вычисляем сайд-поты
                side_pots = self.action_handler.calculate_side_pots()  

                # Раздаем банк
                self.distributive_winnings(winners, side_pots)  

                print("Игра завершена!")
                return  # Завершаем игру

            # Проверяем активных игроков (без фолда)
            active_players = [p for p in self.players if not p.folded]

            # Если в игре остался только один игрок, он выигрывает
            if len(active_players) == 1:
                print(f"{active_players[0].name} выигрывает раздачу, так как все сбросили карты!")
                return  # Завершаем раздачу

            # Разделяем игроков на тех, у кого есть деньги и кто не сделал all-in, и тех, кто остался с all-in
            players_with_money = [p for p in active_players if p.balance > 0 and not p.is_all_in]
            all_in_players = [p for p in active_players if p.is_all_in]

            # Если нет игроков с деньгами, но есть all-in'щики, продолжаем игру
            if not players_with_money and all_in_players:
                print("Все ставки сделаны!")
                round_active = False  # Выходим из метода, но не завершаем раунд

            # Если все ставки уравнены и нет игроков с деньгами, завершаем раунд
            elif not players_with_money and all(p.current_bet == self.current_bet for p in active_players):
                print("Раунд ставок завершен!")
                round_active = False

            # Если раунд только начался, завершаем его
            elif self.dealer.round_counter == 1:
                round_active = False

            # В BettingRound.place_bets() после завершения раунда
            if not players_with_money and all_in_players:
                print("Все ставки сделаны!")
                side_pots = self.action_handler.calculate_side_pots()  # Добавляем сайд-поты
                winners = self.determine_winners()  # Определяем победителя
                self.distributive_winnings(winners, side_pots)  # Раздаем банк
                return  # Завершаем игру

            # После обновления ставки в handle_all_in()
            if all(p.is_all_in or p.folded for p in self.betting_round.players):
                print("Все игроки выставились! Завершаем ставки.")
                return self.betting_round.place_bets()



    def distributive_winnings(self, winners, side_pots):
        if not winners:
            print("Ошибка! Нет победителей!")
            return

        distributed = 0
        for side_pot in side_pots:
            eligible_winners = [
                p for p in winners if p.all_in_amount >= side_pot]
            distributed += self.pot_manager.split_pot(
                side_pot, eligible_winners)

        remaining_pot = self.pot_manager.pot - distributed
        if remaining_pot > 0:
            self.pot_manager.split_pot(remaining_pot, winners)

        print(f"Банк {self.pot_manager.pot} успешно распределен!")
        self.pot_manager.pot = 0

    def start_new_round(self):
        self.players = [player for player in self.players if player.balance > 0 or player.is_all_in]

        if len(self.players) < 2:
            print("Игра окончена! Недостаточно игроков!")
            return
        
        if all(p.is_all_in or p.folded for p in self.players):
            print("Все ставки сделаны! Определяем победителя.")
            return
        
        for player in self.players:
            player.folded = False

        self.current_bet = 0
        self.pot_manager.pot = 0
        print("Новый раунд начался!")
        self.place_bets()
