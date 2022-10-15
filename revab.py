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
    WRONG_POINTS = 0
    CORRECT_POINTS = 10
    
    normalized_guess = guess.strip().lower()
    revabs = all_possible_words_for_abbreviation(abbrev, words)

    if len(revabs) != 0 and normalized_guess == ".":
        return GuessOutcome.NONE_IS_INCORRECT, WRONG_POINTS
    
    if len(revabs) == 0 and normalized_guess == ".":
        return GuessOutcome.NONE_IS_CORRECT, CORRECT_POINTS
    
    if normalized_guess not in words:
        return GuessOutcome.INVALID_WORD, WRONG_POINTS
    
    if normalized_guess not in revabs:
        return GuessOutcome.NOT_REVAB, WRONG_POINTS
    
    sorted_revab_lengths = sorted({len(word) for word in revabs})
    lengths_to_points = {length: CORRECT_POINTS-index for index, length in enumerate(sorted_revab_lengths)}
    user_points = lengths_to_points[len(normalized_guess)]

    # print(lengths_to_points)

    if user_points == CORRECT_POINTS:
        return GuessOutcome.BEST_WORD, CORRECT_POINTS
    
    return GuessOutcome.REVAB_BUT_NOT_BEST, max(user_points, 3)

def generate_abbrev(abbrev_length=3):
    letters = "abcdefghijklmnopqrstuvwxyz"
    return "".join([random.choice(letters) for _ in range(abbrev_length)])

def play_game(words, rounds=5, abbrev_length=3, tries_per_round=3):
    #sum of points across all their rounds
    game_points = 0
    #play certain number of rounds
    for _ in range(rounds):
        #generate abbrev
        abbrev = generate_abbrev(abbrev_length)

        #points in a round is the max of the user's guesses
        round_points = 0
        for _ in range(tries_per_round):
            user_guess = input(f"Enter the shortest revab for {abbrev}, or type . if you think none exist: ")
            outcome, points_on_guess = check_user_guess(abbrev, user_guess, words)
            round_points = max(round_points, points_on_guess)

            if outcome == GuessOutcome.BEST_WORD:
                print(f"Congratulations! {user_guess} is the shortest revab of {abbrev}.")
                break
            elif outcome == GuessOutcome.NONE_IS_CORRECT:
                print(f"Congratulations! There is no revab of {abbrev}.")
                break
            elif outcome == GuessOutcome.REVAB_BUT_NOT_BEST:
                print(f"Good job! {user_guess} is a revab of {abbrev}, but it's not the shortest. This guess is worth {points_on_guess} points.")
            elif outcome == GuessOutcome.NONE_IS_INCORRECT:
                print(f"Wrong! There is a revab for {abbrev}.")
            elif outcome == GuessOutcome.NOT_REVAB:
                print(f"Unfortunately, {user_guess} is not a revab of {abbrev}.")
            elif outcome == GuessOutcome.INVALID_WORD:
                print(f"Unfortunately, {user_guess} is not a valid word according to our dictionary.")
        
        game_points += round_points
        print(f"The shortest revab was {shortest_word_for_abbreviation(abbrev, words)}.")
        print(f"You scored {round_points} last round.")
        print(f"Your current score is {game_points}.")
    
    print(f"Your final score is {game_points}!")
    return game_points

#best word gets most points
#words with same length are a tie
#shortest word(s) get ten points
#second shortest get nine points, and so on
#if they don't get any word, they get zero points

if __name__ == "__main__":
    #http://www.gwicks.net/dictionaries.htm
    #english list with 84_000 words
    #I then fixed words that had é (like éclat), and fixed start of line 1541
    with open("words.txt") as f:
        words = {line.strip() for line in f}

    play_game(words)

