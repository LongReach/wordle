def get_alphabet() -> list:
    return [chr(i) for i in range(ord("a"), ord("z") + 1)]


def create_word_list() -> list:
    """
    Builds a list of allowable words by reading in a text file.
    """
    with open('FiveLetterWords.txt') as f:
        lines = f.readlines()

    alphabet = get_alphabet()
    word_set = set()
    word_list = []

    for line in lines:
        word = line.strip().lower()
        # Remove entries with non-letter characters
        valid = True
        for let in word:
            if let not in alphabet:
                valid = False
                break

        if valid:
            # in case duplicates
            if word not in word_set:
                word_set.add(word)
                word_list.append(word)

    word_list.sort()
    return word_list


def determine_word_scores_1(word_list: list) -> dict:
    """
    Assign a score to each word, method 1. This is done by looking at each letter and counting
    the number of times it's present at the same position in other words in the lexicon. Then
    all five counts are added up.

    The idea is the highest-scoring word is most likely to have letters in common with other
    words in the lexicon (or some subset of it)

    :param word_list: the word list
    :return: a dictionary mapping words to scores
    """
    alphabet = get_alphabet()
    word_scores = {}

    # A list of dictionaries of {letter: count}, one for each positions
    letter_counts = []
    # A list of tuples of (best score, best letter)
    best_letters = []
    for i in range(5):
        the_dict = {}
        for a in alphabet:
            the_dict[a] = 0
        letter_counts.append(the_dict)
        best_letters.append((0, 'a'))

    for word in word_list:
        for i, c in enumerate(word):
            letter_counts[i][c] += 1

    # Take 's' out of the running for the last character
    # letter_counts[4]['s'] = 0

    for word in word_list:
        score = 0
        for i, c in enumerate(word):
            count = letter_counts[i][c]
            score += count
            tup = best_letters[i]
            if count > tup[0]:
                best_letters[i] = (count, c)
        word_scores[word] = score
    # print("total words are", len(word_list))
    # print("best letters are", best_letters)
    return word_scores


def determine_word_scores_2(word_list: list) -> dict:
    """
    Assign a score to each word, method 2. This is done by looking at each letter and counting
    the number of times it's present in the lexicon as a whole, ignoring position.

    The idea is the highest-scoring word is most likely to have letters in common with other
    words in the lexicon (or some subset of it)

    :param word_list: the word list
    :return: a dictionary mapping words to scores
    """
    alphabet = get_alphabet()
    word_scores = {}

    # A dictionary mapping letter to count
    letter_count = {}
    # A tuple of (best score, best letter)
    best_letter = (0, 'a')

    for word in word_list:
        for i, c in enumerate(word):
            if letter_count.get(c) is None:
                letter_count[c] = 0
            letter_count[c] += 1

    for word in word_list:
        score = 0
        for i, c in enumerate(word):
            count = letter_count[c]
            score += count
            tup = best_letter
            if count > tup[0]:
                best_letter = (count, c)
        word_scores[word] = score
    # print("total words are", len(word_list))
    # print("best letter is", best_letter)
    return word_scores


def determine_word_scores(word_list: list, scoring_method) -> dict:
    """
    Assigns a score to each word in lexicon, depending on score method
    :param word_list: the lexicon, as list
    :param scoring_method: 1 or 2, see functions above for details
    :return:
    """
    score_dict = None
    if scoring_method == 1:
        score_dict = determine_word_scores_1(word_list)
    else:
        score_dict = determine_word_scores_2(word_list)

    # Figure out range of scores
    lowest_score = 100000
    lowest_score_word = None
    highest_score = 0
    highest_score_word = None
    for word in word_list:
        if score_dict[word] < lowest_score:
            lowest_score = score_dict[word]
            lowest_score_word = word
        if score_dict[word] > highest_score:
            highest_score = score_dict[word]
            highest_score_word = word

    # Here, we do something a bit clever and turn absolute scores into percentages
    # We'll be able to use this later for a little fuzzy math
    new_score_dict = {}
    for word in word_list:
        pct = float(score_dict[word] - lowest_score) * 100.0 / float(highest_score - lowest_score)
        new_score_dict[word] = pct
        # print(f"Score for {word} is {pct}")

    return new_score_dict

def to_string(array, commas=False):
    """
    Given an array of strings or single characters, produce a human-readable string
    :param array: the input list
    :param commas: if True, then commas will separate items in the string
    :return: the string
    """
    ret_str = ""
    comma_str = ", " if commas else ""
    for c in array:
        let = "_" if c is None else c
        if len(ret_str) == 0:
            ret_str = f"{let}"
        else:
            ret_str += f"{comma_str}{let}"
    return ret_str

def hint_helper(hint_params: str):
    """
    Provides a list of usable words for a real-life Wordle puzzle, given constraints included in
    hint params. Example: "y5o-2rl1:c"

    Part before the colon:
    For each character in the string, if it's a letter alone, it's a yellow letter. If it's a letter
    followed by a positive number, then it's a green letter at that position. If it's a letter followed
    by a negative number, then it's a yellow letter NOT at the position.

    Part after the colon:
    All letters listed are grays

    :param hint_params: the params string
    """
    param_sections = hint_params.split(":")

    # process the gray letters specified
    gray_letters = set()
    if len(param_sections) > 1:
        for c in param_sections[1]:
            gray_letters.add(c)

    # process the yellow and green letters specified
    numerals = [chr(i) for i in range(ord("1"), ord("5") + 1)]
    alphabet = get_alphabet()
    green_letters = [None for i in range(5)]
    yellow_letters = set()
    yellow_letters_exclude_positions = {}
    for c in alphabet:
        yellow_letters_exclude_positions[c] = [False for i in range(5)]
    idx = 0
    while idx < len(param_sections[0]):
        was_green = False
        if hint_params[idx] not in alphabet:
            # An error -- alphabet character not where expected
            idx += 1
            continue
        if (idx < len(hint_params) - 1) and hint_params[idx+1] in numerals:
            # A character with a positive number following, therefore green
            pos = int(hint_params[idx+1]) - 1
            green_letters[pos] = hint_params[idx]
            was_green = True
            idx += 2
            continue
        if not was_green:
            # A yellow letter. Does negative number follow?
            let = hint_params[idx]
            yellow_letters.add(hint_params[idx])
            if (idx < len(hint_params) - 2) and hint_params[idx + 1] == "-":
                pos = int(hint_params[idx + 2]) - 1
                yellow_letters_exclude_positions[let][pos] = True
                idx += 3
            else:
                idx += 1

    usable_words = []
    word_list = create_word_list()
    for word in word_list:
        keep = True
        for i, c in enumerate(word):
            if (green_letters[i] is not None) and (green_letters[i] != c):
                keep = False
                break
            if c in gray_letters:
                keep = False
                break
        for let in yellow_letters:
            if let not in word:
                keep = False
                break
            for i, c in enumerate(word):
                if c == let and yellow_letters_exclude_positions[let][i]:
                    keep = False
                    break
        if keep:
            usable_words.append(word)

    print(f"Green letters: {to_string(green_letters)}")
    print(f"Yellow letters: {to_string(yellow_letters, True)}")
    print("Compatible words:")
    for word in usable_words:
        print(word)

