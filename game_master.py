from random import randrange
from typing import Tuple
from lexicon import to_string

class GameMaster:
    """
    This class runs the game, handling player guesses and doing all necessary record-keeping.
    """
    word_list = []
    word_scores = {}
    alphabet = []

    def __init__(self):
        self.guesses_left = 0
        self.correct_word = None
        self.last_guess = None
        self.definite_letters = None
        self.eliminated_letters = None
        self.misplaced_letters = None
        self.misplaced_letter_count = None
        self.misplaced_letter_map = None
        self.reset()
        self.allow_non_words = False

    def reset(self):
        """
        Call before starting a new game, to reset data.
        """
        word_list_size = len(self.word_list)
        self.guesses_left = self.total_guesses = 6
        self.correct_word = None if word_list_size == 0 else self.word_list[randrange(word_list_size)]
        self.last_guess = None
        self.definite_letters = [None for i in range(5)]
        # Letters no longer usable, though they might have been correct choices earlier
        self.eliminated_letters = set()
        # Misplaced = right letter, wrong position
        self.misplaced_letters = set()
        # The minimum number of times the letter appears in the word
        self.misplaced_letter_count = {}
        # Maps a letter to an list of True/False marking where it has/hasn't been tried.
        self.misplaced_letter_map = {}
        for c in self.alphabet:
            self.misplaced_letter_count[c] = 0
            self.misplaced_letter_map[c] = [False for i in range(5)]

    def get_score(self):
        return self.total_guesses - self.guesses_left

    def handle_guess(self, guess: str) -> Tuple[bool, list, list, list]:
        """
        Handles a guess from the player. Returns lists of green, yellow, and gray letters,
        where green letters are in the right place, yellow letters are in the answer word,
        but the wrong place in the guess word, and gray letters aren't in the word at all.

        In each list, the letter's position corresponds to its place in the guess word.
        If no letter of that color was present at the position, then the value is None.

        :param guess: string containing the guess
        :return: tuple containing (True if guess was acceptable,
        """
        if not self.allow_non_words and guess not in self.word_list:
            print("Not a valid word!")
            return False, [], [], []

        """
        Process:
        1. Mark any green letters in the guess, cross them off in the goal word (so they can't be marked yellow)
        2. Mark any yellow letters in the guess, crossing each off in the goal word. This step goes from left
           to right. If the player guesses the same letter twice and that letter in in the goal word twice,
           then there will be two yellows.
        3. Mark any gray letters in the guess.
        4. Update the overall list of definite letters.
        5. Update the overall list of misplaced letters.
        6. Update the overall list of eliminated letters.
        """

        guess_array = [c for c in guess]
        correct_word_array = [c for c in self.correct_word]
        green_letters = [None for i in range(5)]
        gray_letters = [None for i in range(5)]
        yellow_letters = [None for i in range(5)]

        # Determine all greens, remove these letters (in final word) as option for yellows
        for i in range(5):
            let = guess_array[i]
            if let == correct_word_array[i]:
                green_letters[i] = let
                correct_word_array[i] = None

        # Find yellows and grays
        # From the internet:
        #    If you guess a repeated letter more times than it appears in the word of the day,
        #    the first use of that letter will turn yellow and the second will turn gray,
        for i in range(5):
            let = guess_array[i]
            if let != green_letters[i]:
                if let in correct_word_array:
                    yellow_letters[i] = let
                    # eliminate the letter in the target word so it won't be flagged by
                    # another yellow
                    idx = correct_word_array.index(let)
                    correct_word_array[idx] = None
                else:
                    gray_letters[i] = let

        # Add any greens to definite list
        for i, c in enumerate(green_letters):
            if c is not None:
                if self.definite_letters[i] is None:
                    # This green letter was not previously recorded as a definite
                    # Remove it from tracking as a misplaced letter (if there)
                    if c in self.misplaced_letters:
                        self.misplaced_letter_count[c] -= 1
                        pos_list = self.misplaced_letter_map[c]
                        pos_list[i] = True
                        if self.misplaced_letter_count[c] == 0:
                            # This is no longer a misplaced letter at all
                            self.misplaced_letters.remove(c)
                            # Restore to fully untried
                            for n in range(5):
                                pos_list[n] = False
                self.definite_letters[i] = c

        """
        Add any yellows to misplaced list. Reasoning by example:

        Two yellows for a "b" imply at least two Bs, maybe more. As long as the number of 
        untried slots for "b" equals or exceeds two, then we know that there are two Bs yet
        to be placed. When a B lands in the right slight and turns green, then we drop the
        count by one.
        """
        misplaced_counts_in_turn = {}
        for i, c in enumerate(yellow_letters):
            if c is not None:
                self.misplaced_letters.add(c)
                if misplaced_counts_in_turn.get(c) is None:
                    misplaced_counts_in_turn[c] = 0
                misplaced_counts_in_turn[c] += 1
                pos_list = self.misplaced_letter_map[c]
                pos_list[i] = True
        for c, count in misplaced_counts_in_turn.items():
            if self.misplaced_letter_count[c] < misplaced_counts_in_turn[c]:
                self.misplaced_letter_count[c] = misplaced_counts_in_turn[c]

        # Add any grays to the eliminated list
        for i, c in enumerate(gray_letters):
            if c is not None:
                if c not in self.misplaced_letters:
                    self.eliminated_letters.add(c)

        self.guesses_left -= 1
        self.last_guess = guess
        return True, gray_letters, yellow_letters, green_letters

    def get_all_yellow_patterns(self):
        """
        For all currently known misplaced letters, return a string containing the letter
        at all positions where placeable. If not placeable, then put in "_" instead.
        :return: list of strings, one for each letter
        """
        ret_list = []
        for let in self.misplaced_letters:
            entry = ""
            pos_list = self.misplaced_letter_map.get(let)
            for tried in pos_list:
                if tried:
                    entry += "_"
                else:
                    entry += let
            ret_list.append(entry)
        return ret_list

    def get_hint(self):
        """
        Prints a hint for the player.
        """
        self.print_data()
        usable_words = self.get_usable_words()
        print(f"There are {len(usable_words)} valid choices")
        if len(usable_words) > 5:
            hint = usable_words[randrange(len(usable_words))]
            print(f"Hint word is: {hint}")

    def print_data(self):
        """
        Prints data about game in progress.
        """
        print("unplaced:", to_string(self.get_all_yellow_patterns(), True))
        print("definite:", to_string(self.definite_letters, True))
        print("eliminated:", to_string(self.eliminated_letters, True))

    def get_usable_words(self):
        """
        Returns a list of all words in master list that are still usable, given
        successfully placed, misplaced, and eliminated letters.
        :return: the list
        """
        usable_words = []
        for word in self.word_list:
            keep = True
            # Eliminate words with unusable letters or letters that don't align with "definite" letters
            for i, c in enumerate(word):
                if (self.definite_letters[i] is not None) and (self.definite_letters[i] != c):
                    keep = False
                    break
                if c in self.eliminated_letters:
                    if c not in self.definite_letters:
                        keep = False
                        break

            # Make sure misplaced letters are present in reasonable places
            for let in self.misplaced_letters:
                if let in word:
                    # Letter is in the word, but is it an untried slot?
                    found_slot = False
                    pos_list = self.misplaced_letter_map.get(let)
                    for i, tried in enumerate(pos_list):
                        if not tried and word[i] == let:
                            found_slot = True
                            break
                    if not found_slot:
                        keep = False
                        break
                else:
                    keep = False
                    break
            if keep:
                usable_words.append(word)
        return usable_words

    def select_usable_word(self, usable_words: list):
        best_score = 0
        best_word = None
        for word in usable_words:
            score = self.word_scores[word]
            if score > best_score:
                best_score = score
                best_word = word
        return best_word

    def _count_possible_slots_for_misplaced_letter(self, letter):
        """
        Returns count of number of slots in which letter can still be placed.
        """
        pos_list = self.misplaced_letter_map[letter]
        count = 0
        for tried in pos_list:
            count += 0 if tried else 1
        return count

