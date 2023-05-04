from revabapp.src.revab import check_user_guess
import re

EMPTY = "..."

def validate_round_history(round_history, rounds):
    """
    Return True if round_history is in valid format, False otherwise
    """
    if type(round_history) != list:
        return False
    
    #length of round history should be the number of rounds
    if len(round_history) != rounds:
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
    
    with open("words.txt") as f:
        words = {line.strip() for line in f}
    #all scores should be ints, and the points from best_guess on the abbrev should match the score listed
    for round in round_history:
        score = round["score"]
        if score == EMPTY:
            continue

        if type(score) != int:
            return False
        
        _, correct_score = check_user_guess(round["abbrev"], round["best_guess"], words)
        if score != correct_score:
            return False
    
    return True
        
def validate_guess_history(guess_history, attempts_per_round, abbrev):
    """
    Return True if guess_history is in a valid format, False otherwise
    """
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
    with open("words.txt") as f:
        words = {line.strip() for line in f}
    for guess in guess_history:
        user_guess = guess["guess"]
        if user_guess == EMPTY:
            continue

        if user_guess == "No revabs exist":
            #a period tells 'check_user_guess' that the user thinks no revabs exist
            user_guess = "."
        outcome, score = check_user_guess(abbrev, user_guess, words)
        if guess["result"] != outcome.value:
            return False
        if guess["score"] != score:
            return False

    return True