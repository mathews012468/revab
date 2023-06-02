from revabapp.src.revab import check_user_guess, load_words, NO_REVABS_POSSIBLE
import re
import json

EMPTY = "..."
NO_REVABS_GUESS_MESSAGE = "No revabs exist"

def validate_input(value, pattern):
    """
    Return True if value is not None, a str, and if it matches the pattern
    pattern: raw string that's a regular expression
    """
    if value is None:
        return False
    
    if type(value) != str:
        return False
    
    if not re.match(pattern, value):
        return False
    
    return True

def validate_rounds(rounds):
    """
    Return True if rounds is a one or two digit number, False otherwise
    """    
    rounds_pattern = r'^[123456789][0123456789]?$'
    return validate_input(rounds, rounds_pattern)

def validate_attempts_per_round(attempts_per_round):
    """
    Return True if attempts_per_round is a number from 1 to 5, False otherwise
    """    
    attempts_per_round_pattern = r'^[12345]$'
    return validate_input(attempts_per_round, attempts_per_round_pattern)

def validate_abbrev_length(abbrev_length):
    """
    Return True if abbrev_length is 3 or 4, False otherwise
    """
    abbrev_length_pattern = r'^[34]$'
    return validate_input(abbrev_length, abbrev_length_pattern)

def validate_abbrev(abbrev):
    """
    Return True if abbrev consists of 3 or 4 letters, False otherwise
    """
    abbrev_pattern = r'^[a-zA-Z]{3,4}$'
    return validate_input(abbrev, abbrev_pattern)

def validate_guess(guess):
    """
    Return True if guess is at most 25 characters, False otherwise
    """
    guess_pattern = r'^[a-zA-Z]{1,25}$'
    return validate_input(guess, guess_pattern)

def validate_total_points(total_points):
    """
    Return True if total_points is a 1 to 3 digit number, False otherwise
    """
    total_points_pattern = r'^\d{1,3}$'
    return validate_input(total_points, total_points_pattern)

def validate_round_history(round_history, rounds=None):
    """
    Return True if round_history is in valid format, False otherwise
    """
    if round_history is None:
        return False
    
    if type(round_history) != str:
        return False
    
    try:
        round_history = json.loads(round_history.replace("\'", "\""))
    except json.JSONDecodeError:
        return False
    
    if type(round_history) != list:
        return False
    
    #length of round history should be the number of rounds
    if len(round_history) != rounds and rounds is not None:
        return False
    
    #each element in round history should be a dict with the keys 'number', 'abbrev', 'best_guess', and 'score'
    for round in round_history:
        if type(round) != dict:
            return False
        
        if set(round.keys()) != {"number", "abbrev", "best_guess", "score"}:
            return False
        
    #each number should be one more than the index of its round
    for index, round in enumerate(round_history):
        if round["number"] != index + 1:
            return False
        
    #either all or none of 'abbrev', 'best_guess', and 'score' should be '...'
    #if one round is all '...', then all of the following rounds should be '...' as well
    is_future_round = False
    for round in round_history:
        round_info = {round["abbrev"], round["best_guess"], round["score"]}

        #some fields are filled, some fields are empty. This shouldn't happen
        if EMPTY in round_info and len(round_info) > 1:
            return False

        #this is a round that comes after an empty one but it is non-empty. This shouldn't happen
        if is_future_round and EMPTY not in round_info:
            return False
        
        #any round that comes after this one should have all empty fields
        if EMPTY in round_info:
            is_future_round = True

    #all 'abbrev's that aren't '...' should be the same length, either 3 or 4 letters (alphabetical)
    abbrev_pattern = r'^[a-zA-Z]{3,4}$'
    for round in round_history:
        abbrev = round["abbrev"]
        if abbrev == EMPTY:
            continue

        if type(abbrev) != str:
            return False
        
        if not re.match(abbrev_pattern, abbrev):
            return False

    #all 'best_guess' should be strings (but no restrictions on their content)
    for round in round_history:
        if type(round["best_guess"]) != str:
            return False
    
    words = load_words()
    #all scores should be ints, and the points from best_guess on the abbrev should match the score listed
    for round in round_history:
        score = round["score"]
        if score == EMPTY:
            continue

        if type(score) != int:
            return False
        
        #there is a special string I use to submit user guess when they say that no revabs exist,
        # and I don't display that string in the round history (when it is the best guess that round).
        # Instead of submitting the displayed guess, I submit the special "no revabs" string.
        guess = round["best_guess"]
        if round["best_guess"] == NO_REVABS_GUESS_MESSAGE:
            guess = NO_REVABS_POSSIBLE
        _, correct_score = check_user_guess(round["abbrev"], guess, words)
        if score != correct_score:
            return False

    return True
        
def validate_guess_history(guess_history, attempts_per_round, abbrev):
    """
    Return True if guess_history is in a valid format, False otherwise
    """
    if guess_history is None:
        return False
    
    if type(guess_history) != str:
        return False
    
    try:
        guess_history = json.loads(guess_history.replace("\'", "\""))
    except json.JSONDecodeError:
        return False

    if type(guess_history) != list:
        return False

    #length of guess history should be the number of allowed guessed per round
    if len(guess_history) != attempts_per_round:
        return False

    #each element in guess history should be a dict with the keys 'number', 'guess', 'result', and 'score'
    for guess in guess_history:
        if type(guess) != dict:
            return False
        
        if set(guess.keys()) != {"number", "guess", "result", "score"}:
            return False

    #each number should be one more than the index of its guess
    for index, guess in enumerate(guess_history):
        if guess["number"] != index + 1:
            return False

    #either all or none of 'guess', 'result', and 'score' should be '...'
    #if one guess is all '...', then all of the following guesses should be '...' as well
    is_future_guess = False
    for guess in guess_history:
        guess_info = {guess["guess"], guess["result"], guess["score"]}

        #some fields are filled, some fields are empty. This shouldn't happen
        if EMPTY in guess_info and len(guess_info) > 1:
            return False

        #this is a guess that comes after an empty one but it is non-empty. This shouldn't happen
        if is_future_guess and EMPTY not in guess_info:
            return False
        
        #any guess that comes after this one should have all empty fields
        if EMPTY in guess_info:
            is_future_guess = True

    #all guesses should be strings
    for guess in guess_history:
        if type(guess["guess"]) != str:
            return False
        
    #result and score should match what we get from checking the user's guess against the abbrev
    words = load_words()
    for guess in guess_history:
        user_guess = guess["guess"]
        if user_guess == EMPTY:
            continue

        if user_guess == NO_REVABS_GUESS_MESSAGE:
            user_guess = NO_REVABS_POSSIBLE
        outcome, score = check_user_guess(abbrev, user_guess, words)
        if guess["result"] != outcome.value:
            return False
        if guess["score"] != score:
            return False

    return True