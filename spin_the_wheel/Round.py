from typing import Tuple

from player import Player
from RoundCLI import RoundCLI
from menu import Menu, InvalidMenuOption
from words import SecretWord, InvalidLetter, HasGuessedLetterBefore, NothingLeftToGuess
from Wheel import Wheel
from helpers import sleep


class Round:
    __GUESS_TYPE_WHEEL = 'wheel'
    __GUESS_TYPE_BUY = 'buy'

    def __init__(self, secret_word: SecretWord, players: Tuple[Player, ...] = None):
        self._set_players(players)
        self._set_wheel()
        self._set_secret_word(secret_word)
        self._set_menu()

    def _set_players(self, players):
        if players is None:
            players = tuple([Player("Player")])
        self._players = players
        self._players_count = len(self._players)
        self._current_player_index = 0
        self._current_player = self._players[0]

    def _set_wheel(self):
        self._wheel = Wheel([100, 200, 300, 400, 500])
        self._letter_value = 0

    def _set_secret_word(self, secret_word):
        self._secret_word = secret_word
        self._guessed_letters = []

    def _set_menu(self):
        self._menu = Menu('Escolha uma das opções:', {
            '1': {
                'description': 'Rodar a roda (chutar uma consoante)',
                'action': self._spin_the_wheel
            }
        })

    def run(self):
        return self._run_turn()

    def _run_turn(self):
        self._print_turn_start_message()
        self._input_options_menu()

    def _print_turn_start_message(self):
        RoundCLI.print_start_message(self._secret_word, self._current_player)

    def _input_options_menu(self):
        try:
            option_action = self._menu.input_menu()
            option_action()
        except InvalidMenuOption as e:
            print(e)
            sleep(1)
            self._run_turn()
            return

    def _spin_the_wheel(self):
        self._letter_value = self._wheel.spin()
        self._try_to_guess(Round.__GUESS_TYPE_WHEEL)

    def _try_to_guess(self, guess_type):
        self._print_turn_start_message()
        RoundCLI.print_letter_value_message(self._letter_value)
        try:
            guess = RoundCLI.input_guess()
            has_guessed_letter = self._check_guess(guess, guess_type)
            self._check_round(has_guessed_letter)
        except (InvalidLetter, HasGuessedLetterBefore) as error_message:
            print(error_message)
            sleep(1.5)
            self._try_to_guess(guess_type)
        except NothingLeftToGuess as error_message:
            print(error_message)
            sleep(1.5)

    def _check_guess(self, guess, guess_type):
        print(f"Você chutou '{guess}'")
        letter_count = self._secret_word.get_letter_count(guess)
        has_guessed_letter = self._reveal_letter(guess, guess_type)

        if has_guessed_letter:
            earned_money = self._letter_value * letter_count
            self._current_player.add_money(earned_money)

            RoundCLI.print_guessed_correctly_message(letter_count, guess, earned_money)

        return has_guessed_letter

    def _reveal_letter(self, guess, guess_type):
        if guess_type == Round.__GUESS_TYPE_WHEEL:
            has_guessed_letter = self._secret_word.reveal_consonant_or_number(guess)
        elif guess_type == Round.__GUESS_TYPE_BUY:
            has_guessed_letter = self._secret_word.reveal_vowel(guess)
        else:
            has_guessed_letter = False

        return has_guessed_letter

    def _check_round(self, has_guessed_letter):
        if self._secret_word.was_guessed:
            return

        RoundCLI.print_end_turn_message(has_guessed_letter)
        if has_guessed_letter:
            return self._continue_turn()
        else:
            return self._next_turn()

    def _continue_turn(self):
        return self._run_turn()

    def _next_turn(self):
        self._select_next_player()
        return self._run_turn()

    def _select_next_player(self):
        next_player_index = self._current_player_index + 1
        index_is_out_of_bounds = next_player_index >= self._players_count

        if index_is_out_of_bounds:
            next_player_index = 0

        self._current_player_index = next_player_index
        self._current_player = self._players[next_player_index]
