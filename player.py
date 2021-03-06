from typing import Tuple
from enum import Enum
from game_master import GameMaster
from lexicon import to_string


class GuessOutcomeCode(Enum):
    """
    Enumerator representing possible outcomes of a single turn.
    """
    UNDECIDED = 0
    VICTORY = 1
    DEFEAT = 2
    QUIT = 3
    ERROR = 4

    def is_game_end(self):
        return self != GuessOutcomeCode.UNDECIDED

class Player:
    """
    This class represents the game player. It can either manage a game for a human player
    or play automatically itself.
    """

    def __init__(self, game_master: GameMaster, human_player: bool):
        self.game_master = game_master
        self.automatic_play = not human_player
        self.debug_mode = False

    def handle_guess(self) -> GuessOutcomeCode:
        """
        Makes a single guess or handles one from human player.
        :return: GuessOutcomeCode
        """
        if self.automatic_play:
            return self._handle_robot_guess()
        else:
            return self._handle_human_guess()

    def print_help(self):
        """
        Prints out the user manual.
        """
        print("\nManual:")
        print("Enter your word guess or use one of the following commands:")
        print("'q' or 'exit': Exit game")
        print("'hint': Get a hint")
        print("'answer': Show the answer")
        print("'nonwords': Allow non-words to be guesses")
        print("'words': Only words from the dictionary file can be guesses")
        print("'reset' <new word>: Resets the game. If <new word> provided, that becomes the new answer")
        print("'help': Show these instructions")

    def _handle_human_guess(self) -> GuessOutcomeCode:
        """
        Handles a guess from the human player, asking for input, then determining results.
        Also processes any commands the player might type.

        :return: outcome code
        """
        guess_num = self.game_master.total_guesses - self.game_master.guesses_left + 1
        print(f"\nGuess {guess_num}/{self.game_master.total_guesses}")
        guess = input("> ")
        if guess == self.game_master.correct_word:
            print("You win!! Yay.")
            return GuessOutcomeCode.VICTORY
        elif guess == "q" or guess == "exit":
            return GuessOutcomeCode.QUIT
        elif guess == "hint":
            self.game_master.get_hint()
            return GuessOutcomeCode.UNDECIDED
        elif guess == "answer":
            print(f"Answer is: {self.game_master.correct_word}")
            return GuessOutcomeCode.UNDECIDED
        elif guess == "nonwords":
            self.game_master.allow_non_words = True
            return GuessOutcomeCode.UNDECIDED
        elif guess == "words":
            self.game_master.allow_non_words = False
            return GuessOutcomeCode.UNDECIDED
        elif "reset" in guess:
            parts = guess.split(" ")
            print("Resetting game.")
            self.game_master.reset()
            if len(parts) > 1:
                self.game_master.correct_word = parts[1]
            return GuessOutcomeCode.UNDECIDED

        success, gray_letters, yellow_letters, green_letters = self.game_master.handle_guess(guess)
        remaining_letters = [a for a in GameMaster.alphabet if a not in self.game_master.eliminated_letters]
        remaining_letters_str = to_string(remaining_letters, True)
        print(f"Gray letters:   {to_string(gray_letters)}")
        print(f"Green letters:  {to_string(green_letters)}")
        print(f"Yellow letters: {to_string(yellow_letters)}")
        print(f"\nLetters left:   {remaining_letters_str}")
        print(f"Definite:       {to_string(self.game_master.definite_letters)}")
        print(f"All yellows:    {to_string(self.game_master.get_all_yellow_patterns(), True)}")
        return GuessOutcomeCode.UNDECIDED

    def _handle_robot_guess(self) -> GuessOutcomeCode:
        """
        Handles a guess by the AI player. The GameMaster implements a lot of the logic of the heuristic.
        I supposed it makes more sense to be in this class, but oh well.

        :return: the outcome code
        """
        guess_num = self.game_master.total_guesses - self.game_master.guesses_left + 1
        # Choose the strategy. This logic is somewhat arbitrary; I arrived at it via tweaks.
        green_count = 0
        for g in self.game_master.definite_letters:
            if g is not None:
                green_count += 1
        ignore_greens = False
        ignore_yellows = False
        strategy_type = "hone in"
        if (self.game_master.guesses_left > 4) or ((self.game_master.guesses_left > 2) and green_count < 2):
            ignore_greens = True
            strategy_type = "position yellows"
            if len(self.game_master.misplaced_letters) < 2:
                ignore_yellows = True
                strategy_type = "untried letters"

        usable_words = self.game_master.get_usable_words(ignore_greens=ignore_greens, ignore_yellows=ignore_yellows)
        if len(usable_words) == 0:
            print(f"ERROR: no usable words, answer was {self.game_master.correct_word}")
            print("")
            self.game_master.print_data()
            return GuessOutcomeCode.ERROR
        guess = self.game_master.select_usable_word(usable_words)
        success, gray_letters, yellow_letters, green_letters = self.game_master.handle_guess(guess)
        print(f"\nGuess was: {guess}. Turn {guess_num} of {self.game_master.total_guesses}. Strategy: {strategy_type}")
        if guess == self.game_master.correct_word:
            print(f"Victory!")
            return GuessOutcomeCode.VICTORY
        if guess_num >= self.game_master.total_guesses:
            print(f"Out of guesses, game over. Defeat! (Word was {self.game_master.correct_word})")
            return GuessOutcomeCode.DEFEAT
        print(f"Gray letters:   {to_string(gray_letters)}")
        print(f"Green letters:  {to_string(green_letters)}")
        print(f"Yellow letters: {to_string(yellow_letters)}")
        if self.debug_mode:
            self.game_master.print_data()
        return GuessOutcomeCode.UNDECIDED
