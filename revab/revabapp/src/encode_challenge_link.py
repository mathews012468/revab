import base64
from revabapp.src.revab import check_user_guess, load_words, NO_REVABS_POSSIBLE
from revabapp.src.validate import NO_REVABS_GUESS_MESSAGE

#base64 uses characters that aren't url safe. Instead of percent encoding them,
#I provide alternate url-safe characters to use
ALTCHARS = b"_;"
STRING_ENCODING = "utf-8"

#TODO: should I validate in these functions? I think yes!
#NOTE: I intentionally ignore the attempts per round.
def get_challenge_code(name, round_history):
    """
    Go from name and round history to the code that identifies a challenge.
    
    To encode the information required to uniquely identify a challenge,
    I write the name as well as each abbreviation and best guess in a list
    separated by commas:
    name,abbrev1,best_guess1,abbrev2,best_guess2,...
    best_guess gets converted to a period (.) if it's "no revabs possible"
    
    Then I encode that in base64 with the alternate characters _;.
    """
    challenge_info = [name]
    for round in round_history:
        challenge_info.append(round["abbrev"])
        #if the user's best guess in a round was that there were no revabs possible,
        # save the code that represents 'no revabs exist' in my code instead of the
        # message that I normally display to the user in that situation.
        if round["best_guess"] == NO_REVABS_GUESS_MESSAGE:
            challenge_info.append(NO_REVABS_POSSIBLE)
        else:
            challenge_info.append(round["best_guess"])
    challenge_info_string = ",".join(challenge_info)

    #need to convert to bytes before b64encode
    challenge_info_bytes = bytes(challenge_info_string, encoding=STRING_ENCODING)
    encoded_challenge_bytes = base64.b64encode(challenge_info_bytes, altchars=ALTCHARS)

    return str(encoded_challenge_bytes, encoding=STRING_ENCODING)

#go from challenge link to name and round_history
def get_name_and_round_history(challenge_code):
    decoded_challenge_bytes = base64.b64decode(challenge_code, altchars=ALTCHARS)
    challenge_info_string = str(decoded_challenge_bytes, encoding=STRING_ENCODING)

    #avoid reloading words every time we compute the round score
    #need to find the score because the challenge code only has 
    # the abbrev and the guess for each round
    words = load_words()

    #challenge_info should have an odd number of values, and all of the values should
    #have exclusively letters or be a period. Validation should happen somewhere.
    challenge_info = challenge_info_string.split(",")
    round_history = []
    for index in range(1, len(challenge_info), 2):
        number = (index + 1) // 2 #1,2,3,4,...
        abbrev = challenge_info[index]
        best_guess = challenge_info[index + 1]

        _, score = check_user_guess(abbrev, best_guess, words)
        if best_guess == NO_REVABS_POSSIBLE:
            best_guess = NO_REVABS_GUESS_MESSAGE
        round = {
            "number": number,
            "abbrev": abbrev,
            "best_guess": best_guess,
            "score": score
        }
        round_history.append(round)

    name = challenge_info[0]
    return name, round_history
