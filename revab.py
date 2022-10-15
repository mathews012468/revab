import itertools
import random
from enum import Enum

class GuessOutcome(Enum):
    INVALID_WORD = 1
    NOT_REVAB = 2
    REVAB_BUT_NOT_BEST = 3
    BEST_WORD = 4
    NONE_IS_INCORRECT = 5
    NONE_IS_CORRECT = 6

#is_abbreviation is same as is_subsequence
#code adapted from stack overflow answer: https://stackoverflow.com/a/24017597
def is_abbreviation(abbrev, word):
    abbrev, word = abbrev.lower(), word.lower()
    current_pos = 0
    for c in abbrev:
        current_pos = word.find(c, current_pos) + 1
        if current_pos == 0:
            return False
    return True

def all_possible_words_for_abbreviation(abbrev, words):
    return {word.lower() for word in words if is_abbreviation(abbrev, word)}

def shortest_word_for_abbreviation(abbrev, words):
    #for each word in words
    # check if abbrev could be an abbreviation of word
    # add to possible list
    revabs = all_possible_words_for_abbreviation(abbrev, words)

    #for all possible revabs
    # return smallest
    return min(revabs, key=len, default="")

def check_user_guess(abbrev, guess, words):
    #better guess: fewer points
    #if best guess: 1 point
    #if second best guess (and any ties): 2 points
    #third best: 3points, so on
    #not valid: 10 points
    
    normalized_guess = guess.strip().lower()
    if normalized_guess not in words:
        return GuessOutcome.INVALID_WORD, 10
    
    revabs = all_possible_words_for_abbreviation(abbrev, words)

    print(revabs)

    if len(revabs) != 0 and normalized_guess == ".":
        return GuessOutcome.NONE_IS_INCORRECT, 10
    
    if len(revabs) == 0 and normalized_guess == ".":
        return GuessOutcome.NONE_IS_CORRECT, 1
    
    if normalized_guess not in revabs:
        return GuessOutcome.NOT_REVAB, 10
    
    sorted_revab_lengths = sorted({len(word) for word in revabs})
    lengths_to_points = {length: index + 1 for index, length in enumerate(sorted_revab_lengths)}
    user_points = lengths_to_points[len(normalized_guess)]

    if user_points == 1:
        return GuessOutcome.BEST_WORD, 1
    
    return GuessOutcome.REVAB_BUT_NOT_BEST, user_points

def generate_abbrev(abbrev_length=3):
    letters = "abcdefghijklmnopqrstuvwxyz"
    return "".join([random.choice(letters) for _ in range(abbrev_length)])

def play_game(rounds=5, abbrev_length=3, tries_per_round=3):
    #play certain number of rounds
    for _ in range(rounds):
        #generate abbrev
        abbrev = generate_abbrev(abbrev_length)
        #let user guess
        for _ in range(tries_per_round):
            user_guess = input(f"Enter the shortest revab for {abbrev}, or type . if you think none exist: ")
            points_on_guess = check_user_guess(abbrev, user_guess)

        pass
    pass

def main(abbrev):
    #http://www.gwicks.net/dictionaries.htm
    #english list with 84_000 words
    #I then fixed words that had é (like éclat), and fixed start of line 1541
    with open("words.txt") as f:
        words = {line.strip() for line in f}

    revab = shortest_word_for_abbreviation(abbrev, words)
    print(abbrev, revab)

#like golf, best word gets fewest points
#words with same length are a tie
#shortest word(s) get one point
#second shortest get two, and so on
#if they don't get any word, they get ten points

if __name__ == "__main__":
    with open("words.txt") as f:
        words = {line.strip() for line in f}

    while True:
        abbrev = generate_abbrev()
        revabs = all_possible_words_for_abbreviation(abbrev)
        print(revabs)
        input() #pause

        user_guess = input(f"guess {abbrev}: ")
        print( check_user_guess(abbrev, user_guess, words) )