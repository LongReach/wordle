from typing import Tuple
from lexicon import create_word_list, determine_word_scores, get_alphabet
from game_master import GameMaster
from player import Player, GuessOutcomeCode

game_master = GameMaster()
player = Player(game_master, False)


def run_game() -> Tuple[bool, GuessOutcomeCode, int]:
    print("\nBeginning new game\n=======================")
    game_master.reset()
    outcome_code = GuessOutcomeCode.UNDECIDED
    while game_master.guesses_left > 0:
        outcome_code = player.handle_guess()
        if outcome_code.is_game_end():
            break
    score = game_master.get_score()
    return game_master.guesses_left > 0, outcome_code, score


def run_many_games(game_count):
    global game_master, player
    GameMaster.word_list = create_word_list()
    GameMaster.word_scores = determine_word_scores(game_master.word_list)
    GameMaster.alphabet = get_alphabet()
    game_master.reset()
    player.debug_mode = True
    player.print_help()

    victory_count = 0
    defeat_count = 0
    error_count = 0
    average_score = 0.0
    for g in range(game_count):
        victory, outcome_code, score = run_game()
        if outcome_code == GuessOutcomeCode.QUIT:
            print("Quitting.")
            break
        elif outcome_code == GuessOutcomeCode.ERROR:
            error_count += 1
        elif victory:
            victory_count += 1
            average_score = (average_score * float(victory_count) + float(score)) / float(victory_count + 1)
        else:
            defeat_count += 1
    print("\nResults:")
    print(f"Total games:     {game_count}")
    print(f"Total victories: {victory_count}")
    print(f"Total defeats:   {defeat_count}")
    print(f"Total errors:    {error_count}")
    print(f"Average score:   {average_score}")

run_many_games(100)