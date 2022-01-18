from typing import Tuple
import argparse
from lexicon import create_word_list, determine_word_scores, get_alphabet, hint_helper
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


def run_many_games(ai_mode, game_count, scoring_method, debug_mode):
    global game_master, player
    GameMaster.word_list = create_word_list()
    GameMaster.word_scores = determine_word_scores(game_master.word_list, scoring_method)
    GameMaster.alphabet = get_alphabet()
    game_master.reset()
    player.automatic_play = ai_mode
    player.debug_mode = debug_mode
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
    print(f"% victories      {(float(victory_count) / float(game_count)) * 100.0}")
    print(f"Average score:   {average_score}")


parser = argparse.ArgumentParser(description='Wordle Game and Solver', formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument(
    "--ai",
    required=False,
    action="store_true",
    help="Run AI, rather than playing as yourself",
)
parser.add_argument(
    "--games",
    type=int,
    required=False,
    default=None,
    help="How many games to play",
)
parser.add_argument(
    "--debug",
    required=False,
    action="store_true",
    help="Run in debug mode",
)
parser.add_argument(
    "--scoring_method",
    type=int,
    required=False,
    default=1,
    help="Scoring method to use",
)
parser.add_argument(
    "--hint",
    type=str,
    required=False,
    default=None,
    help="Provide candidate words for a real world Wordle game, e.g. --hint y5o-2r-3:cs\n"
         "Meanings (where 'c' represents a letter and 'n' a position number):\n"
         "c   -> a yellow letter\n"
         "c-n -> a yellow letter that's not at position n\n"
         "cn  -> a green letter at position n\n"
         "Anything after ':': a gray letter",
)

args = parser.parse_args()

if args.hint is not None:
    hint_helper(args.hint)
    exit()

num_games = args.games
if num_games is None:
    if args.ai:
        num_games = 100
    else:
        num_games = 1

run_many_games(args.ai, num_games, args.scoring_method, args.debug)

