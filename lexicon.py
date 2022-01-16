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


def determine_word_scores(word_list: list) -> dict:
    """
    Assign a score to each word. This is done by looking at each letter and counting the number
    of times it's present at the same position in other words in the lexicon. Then all five
    counts are added up.

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

    for word in word_list:
        score = 0
        for i, c in enumerate(word):
            count = letter_counts[i][c]
            score += count
            tup = best_letters[i]
            if count > tup[0]:
                best_letters[i] = (count, c)
        word_scores[word] = score
        #print(f"score of word {word} is {score}")
    print("total words are", len(word_list))
    print("best letters are", best_letters)
    return word_scores


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
