# Wordle

## Overview

![](images/WordleMeme1.jpeg)

If you used social media at all in January, 2022, then you've heard of Wordle.

This a puzzle game involving English words. The rules aren't too complex and can be found [here](https://www.powerlanguage.co.uk/wordle/). Basically, there's a five-letter goal word that you have to figure out, and you get six tries in which to do so, typing in guesses and receiving clues as to how close each guess came.

In the web game, for each guess, each letter will be highlighted one of three ways:
* :green_square: Green: this is a correct letter and in the correct position
* :yellow_square: Yellow: this a correct letter, but in the wrong position
* :black_large_square: Black/Gray: this letter is not in the goal word at all

## This Program

I write this program in Python 3.8. It generates a series of Wordle puzzles that you can either play yourself or allow the program to solve automatically, which it attempts to do without cheating.

If you have Python on your system, then put the source files in some folder. Then...

To play a game yourself:
```
$ python3 wordle.py
```

To let the AI play:
```
$ python3 wordle.py --ai
```

To see other options:
```
$ python3 wordle.py --help
```

## AI Implementation

![](images/WordleMeme2.jpg)

My thinking about strategy is thus...

On each turn, you have three basic choices:
1. Choose a word that includes letters you haven't tried before.
2. If you have some number of yellow letters, then choose a word that attempts to find the correct positions for them.
3. Try to solve for the final word, putting whatever green letters you've gotten in the correct positions.

As I see it, in early turns, you want the AI to try to eliminate letters that aren't in the final word, not worrying about greens that much, but trying to get yellows into their final place. In the last two turns, you do want to keep your greens in place, filling in the few (hopefully) remaining positions with your best guesses.

Another feature of my implementation is that each word in the lexicon has a "score" assigned to it. The score reflects how common the letters of the word are in the rest of the lexicon. Whenever the AI has a selection of words to try on a given turn, it should prefer the highest scoring one.

In the real game, I would assume the creator has some cleverness to choosing his goal word. However, in this program, one is simply selected at random.

## Scoring

![](images/Scoring.png)
_Yep, this guy shot down one of his fellow Americans. But, there was a [good reason](https://www.gijobs.com/pilot-shot-down-american-plane/)._

More to follow...