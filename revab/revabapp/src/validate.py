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
        
        _, correct_score = check_user_guess(abbrev, round["best_guess"], words)
        if score != correct_score:
            return False
    
    return True
        
