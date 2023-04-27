import random
from enum import Enum

class GuessOutcome(Enum):
    INVALID_WORD = 1 #not in dictionary
    NOT_REVAB = 2 #valid word, not a revab
    REVAB_BUT_NOT_BEST = 3
    BEST_WORD = 4
    NONE_IS_INCORRECT = 5 #there are revabs, but the user indicated there weren't any
    NONE_IS_CORRECT = 6 #there are no revabs and the user got this right


def _is_abbreviation(abbrev, word):
    """
    Returns True if word is a revab of abbrev, False otherwise
    "is revab" is the same as saying "is subsequence" but in reverse order
    e.g 'anyone' is a revab of 'nye', but not of 'nya'

    abbrev: str
    word: str
    return: bool

    code adapted from stack overflow answer: https://stackoverflow.com/a/24017597
    """
    abbrev, word = abbrev.lower(), word.lower()
    current_pos = 0
    for c in abbrev:
        current_pos = word.find(c, current_pos) + 1
        if current_pos == 0:
            return False
    return True


def _all_possible_words_for_abbreviation(abbrev, words):
    """
    Returns a set of all revabs (lowercased) of abbrev in words.

    abbrev: str
    words: any iterable of strings, but I'm (almost) always passing in a set. Set of all words in dictionary.
    """
    return {word.lower() for word in words if _is_abbreviation(abbrev, word)}


def _shortest_word_for_abbreviation(abbrev, words):
    """
    Returns shortest revab for abbrev in words. 
    If there is a tie, we pick one. 
    If there are none, we return an empty string.

    abbrev: str
    words: set of strings
    return: str
    """
    #for each word in words
    # check if abbrev could be an abbreviation of word
    # add to possible list
    revabs = _all_possible_words_for_abbreviation(abbrev, words)

    #for all possible revabs
    # return smallest
    return min(revabs, key=len, default="")


def _check_user_guess(abbrev, guess, words):
    """
    Determines the outcome of a user guess.
    Return a 2-tuple of a GuessOutcome and number of points earned on the guess.
    A guess has six distinct outcomes that you can find in enum definition above but we duplicate here:

    1. INVALID_WORD #not in dictionary
    2. NOT_REVAB #valid word, not a revab
    3. REVAB_BUT_NOT_BEST
    4. BEST_WORD
    5. NONE_IS_INCORRECT #there are revabs, but the user indicated there weren't any
    6. NONE_IS_CORRECT #there are no revabs and the user got this right

    More points is better. Correct guess gets 10 points, incorrect gets 0 points.
    If user guesses the shortest revab, they get full 10 points.
    If user guesses a revab that is not the shortest, 
    they get points based on how close they were to the shortest.
    Second shortest gets 9 points, third shortest gets 8 points, and so on.
    A valid revab can get no fewer than 3 points.

    abbrev: str
    guess: str
    words: set of strings
    return: (GuessOutcome, int)
    """
    WRONG_POINTS = 0
    CORRECT_POINTS = 10
    
    normalized_guess = guess.strip().lower()
    revabs = _all_possible_words_for_abbreviation(abbrev, words)

    if len(revabs) != 0 and normalized_guess == ".":
        return GuessOutcome.NONE_IS_INCORRECT, WRONG_POINTS
    
    if len(revabs) == 0 and normalized_guess == ".":
        return GuessOutcome.NONE_IS_CORRECT, CORRECT_POINTS
    
    if normalized_guess not in words:
        return GuessOutcome.INVALID_WORD, WRONG_POINTS
    
    if normalized_guess not in revabs:
        return GuessOutcome.NOT_REVAB, WRONG_POINTS
    
    #when we have an ascending sorted list of the lengths of all revabs,
    #the points from a guess is 10 minus the index of the length of the guess
    #(remember, shortest word gets 10 points, and index 0 is shortest length)
    sorted_revab_lengths = sorted({len(word) for word in revabs})
    lengths_to_points = {length: CORRECT_POINTS-index for index, length in enumerate(sorted_revab_lengths)}
    user_points = lengths_to_points[len(normalized_guess)]

    if user_points == CORRECT_POINTS:
        return GuessOutcome.BEST_WORD, CORRECT_POINTS
    
    return GuessOutcome.REVAB_BUT_NOT_BEST, max(user_points, 3)


def generate_abbrev(abbrev_length=3):
    """
    Generate abbreviation for the user to guess.

    abbrev_length: int
    return: str
    """
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    return "".join([random.choice(letters) for _ in range(abbrev_length)])


def play_game(words, rounds=5, abbrev_length=3, tries_per_round=3):
    """
    Play a game of revab.

    words: set of strings, all the words we're playing with in the game.
    rounds: int, number of revabs for the user to guess in a complete game.
    abbrev_length: int, length of abbreviations in each round.
    tries_per_round: int, number of tries for the user to guess each round before moving on to the next.
    return: int, total points scored in game.
    """
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
            outcome, points_on_guess = _check_user_guess(abbrev, user_guess, words)
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
        print(f"The shortest revab was {_shortest_word_for_abbreviation(abbrev, words)}.")
        print(f"You scored {round_points} last round.")
        print(f"Your current score is {game_points}.")
    
    print(f"Your final score is {game_points}!")
    return game_points


if __name__ == "__main__":
    #http://www.gwicks.net/dictionaries.htm
    #english list with 84_000 words
    with open("words.txt") as f:
        words = {line.strip() for line in f}

    play_game(words, rounds=5, abbrev_length=3, tries_per_round=3)
