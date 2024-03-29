from django.shortcuts import render
from django.http import HttpResponse
from revabapp.src.revab import \
    generate_abbrev, \
    check_user_guess, \
    load_words, \
    GuessOutcome, \
    NO_REVABS_POSSIBLE
from revabapp.src.validate import \
    validate_round_history, \
    validate_guess_history, \
    validate_rounds, \
    validate_attempts_per_round, \
    validate_abbrev_length, \
    validate_abbrev, \
    validate_guess, \
    validate_total_points, \
    EMPTY, \
    NO_REVABS_GUESS_MESSAGE
from revabapp.src.encode_challenge_link import \
    get_challenge_code, \
    get_name_and_round_history
import json

# Create your views here.

def index(request):
    context = reasonable_defaults(request)

    save_or_clear = request.POST.get("settings", "default")
    if "default" in save_or_clear:
        context["abbrev_length"] = 3
        context["attempts_per_round"] = 3
        context["rounds"] = 5

    return render(request, "revabapp/index.html", context)

def settings(request):
    #Should not use reasonable_defaults here because it gives default values for all post key-value
    # pairs I use throughout the site, a lot of which only apply to the game and results pages.
    # This is an issue when user visits help page from settings then returns to settings; in that case,
    # reasonable_defaults would see 'abbrev': None and then treat None as a four-letter abbreviation.
    context = {
        "rounds": request.POST.get('rounds'),
        "attempts_per_round": request.POST.get('attempts_per_round'),
        "abbrev_length": request.POST.get('abbrev_length')
    }
    return render(request, "revabapp/settings.html", context)

def stats(request):
    context = {
        "rounds": request.POST.get('rounds'),
        "attempts_per_round": request.POST.get('attempts_per_round'),
        "abbrev_length": request.POST.get('abbrev_length'),
        "settings": request.POST.get('settings'),
        "destination": request.POST.get('destination')
    }
    return render(request, "revabapp/stats.html", context)

def help_page(request):
    context = {
        "rounds": request.POST.get('rounds'),
        "attempts_per_round": request.POST.get('attempts_per_round'),
        "abbrev_length": request.POST.get('abbrev_length'),
        "abbrev": request.POST.get('abbrev'),
        "guess_history": request.POST.get('guess_history'),
        "round_history": request.POST.get('round_history'),
        "opponent_round_history": request.POST.get('opponent_round_history'),
        "opponent_name": request.POST.get('opponent_name'),
        "total_points": request.POST.get('total_points'),
        "settings": request.POST.get('settings'),
        "destination": request.POST.get('destination')
    }

    return render(request, "revabapp/help.html", context)

def game(request):
    context = reasonable_defaults(request)

    #if we come from the help page, just load the page, don't do any computations
    if request.POST.get("source") in {"help", "home", "results"}:
        return render(request, "revabapp/game.html", context)

    #submit user guess
    words = load_words()
    guess_type = request.POST.get('submitbutton')
    #guess is what I submit on behalf of the user, context["user_guess"] is what gets shown
    # on the website. In most cases these should be the same; they're different only when the
    # user thinks that no revabs exist. There is a special string representing the guess
    # "no revabs exist" in code that I don't want to expose to the user.
    guess = context["user_guess"]
    if guess_type != "Guess":
        guess = NO_REVABS_POSSIBLE
        context["user_guess"] = NO_REVABS_GUESS_MESSAGE
    outcome, score = check_user_guess(context["abbrev"], guess, words)
    
    #calculate score
    round_score = 0
    for guess in context["guess_history"]:
        if guess["score"] == EMPTY:
            break
        if guess["score"] > round_score:
            round_score = guess["score"]
    round_score = max(round_score, score)
    
    #update guess history
    if outcome == GuessOutcome.BEST_WORD or outcome == GuessOutcome.NONE_IS_CORRECT:
        #this is my signal that the round is over later on
        context["attempt_number"] = context["attempts_per_round"]
    context["guess_history"][context["attempt_number"] - 1] = {
        "number": context["attempt_number"], 
        "guess": context["user_guess"], 
        "result": outcome.value, 
        "score": score
    }

    #if necessary, update round history and generate new round info
    if context["attempt_number"] == context["attempts_per_round"]:
        context["round_history"][context["round_number"] - 1] = {
            "number": context["round_number"], 
            "abbrev": context["abbrev"], 
            "best_guess": best_guess(context["guess_history"]), 
            "score": round_score
        }
        context["abbrev"] = generate_abbrev(context["abbrev_length"])
        context["total_points"] += round_score
        context["guess_history"] = [{"number": i+1, "guess": EMPTY, "result": EMPTY, "score": EMPTY} for i in range(context["attempts_per_round"])]
        context["round_number"] += 1

    #if game is over, move to results page
    if context["round_number"] > context["rounds"]:
        #path key used to figure out what to display in the last row of the results page
        context["path"] = "results"
        return render(request, "revabapp/results.html", context)

    #else, stay on the game page
    return render(request, "revabapp/game.html", context)

def challenge_game(request):
    #round_history, guess_history, total_points are all fine
    #attempts_per_round is probably good too since I don't
    #provide it a value and the default is 3 (which is what I want)
    context = reasonable_defaults(request)
    context["opponent_name"] = request.POST.get("opponent_name")
    context["abbrev"] = context["opponent_round_history"][context["round_number"] - 1]["abbrev"]

    #if we come from the help page, just load the page, don't do any computations
    if request.POST.get("source") in {"help", "home"}:
        return render(request, "revabapp/challenge-game.html", context)

    #submit user guess
    words = load_words()
    guess_type = request.POST.get('submitbutton')
    #guess is what I submit on behalf of the user, context["user_guess"] is what gets shown
    # on the website. In most cases these should be the same; they're different only when the
    # user thinks that no revabs exist. There is a special string representing the guess
    # "no revabs exist" in code that I don't want to expose to the user.
    guess = context["user_guess"]
    if guess_type != "Guess":
        guess = NO_REVABS_POSSIBLE
        context["user_guess"] = NO_REVABS_GUESS_MESSAGE
    outcome, score = check_user_guess(context["abbrev"], guess, words)
    
    #calculate score
    round_score = 0
    for guess in context["guess_history"]:
        if guess["score"] == EMPTY:
            break
        if guess["score"] > round_score:
            round_score = guess["score"]
    round_score = max(round_score, score)
    
    #update guess history
    if outcome == GuessOutcome.BEST_WORD or outcome == GuessOutcome.NONE_IS_CORRECT:
        #this is my signal that the round is over later on
        context["attempt_number"] = context["attempts_per_round"]
    context["guess_history"][context["attempt_number"] - 1] = {
        "number": context["attempt_number"], 
        "guess": context["user_guess"], 
        "result": outcome.value, 
        "score": score
    }

    #if necessary, update round history and generate new round info
    if context["attempt_number"] == context["attempts_per_round"]:
        context["round_history"][context["round_number"] - 1] = {
            "number": context["round_number"], 
            "abbrev": context["abbrev"], 
            "best_guess": best_guess(context["guess_history"]), 
            "score": round_score
        }
        #avoid an index error when we reach the end of the game
        if context["round_number"] < context["rounds"]:
            context["abbrev"] = context["opponent_round_history"][context["round_number"]]["abbrev"]
        context["total_points"] += round_score
        context["guess_history"] = [{"number": i+1, "guess": EMPTY, "result": EMPTY, "score": EMPTY} for i in range(context["attempts_per_round"])]
        context["round_number"] += 1

    #if game is over, move to results page
    if context["round_number"] > context["rounds"]:
        #need to pass existing context to make sure last round is in the round history
        return display_challenge_results(request, context)

    #else, stay on the game page
    return render(request, "revabapp/challenge-game.html", context)

def display_challenge_results(request, context):
    context["opponent_name"] = request.POST.get("opponent_name")
    context["abbrev_length"] = len(context["round_history"][0]["abbrev"])
    context["total_points"] = sum([round["score"] for round in context["round_history"]])
    context["opponent_total_points"] = sum([round["score"] for round in context["opponent_round_history"]])
    #determine who won
    if context["total_points"] > context["opponent_total_points"]:
        context["result_text"] = "won against"
    elif context["total_points"] == context["opponent_total_points"]:
        context["result_text"] = "tied"
    else:
        context["result_text"] = "lost to"

    return render(request, "revabapp/challenge-results.html", context)

def get_name_for_challenge(request):
    context = reasonable_defaults(request)
    context["path"] = "challenge/name"
    return render(request, "revabapp/results.html", context)

def display_challenge_link(request):
    context = reasonable_defaults(request)
    #NOTE: name cannot have commas! Add validation
    context["name"] = request.POST.get("name")
    context["path"] = "challenge/link"
    challenge_code = get_challenge_code(context["name"], context["round_history"])
    context["link"] = f"http://revab.us/challenge/start/{challenge_code}"

    return render(request, "revabapp/results.html", context)

def start_challenge(request, challenge_code):
    opponent_name, opponent_round_history = get_name_and_round_history(challenge_code)
    rounds = len(opponent_round_history)
    context = {
        "opponent_name": opponent_name,
        "opponent_round_history": opponent_round_history,
        "rounds": rounds
    }
    return render(request, "revabapp/challenge-start.html", context)

def reasonable_defaults(request):
    """
    Take in a request object from django and return a dict
    with reasonable defaults for most common post form keys
    """
    rounds = request.POST.get("rounds")
    if not validate_rounds(rounds):
        rounds = "5"
    rounds = int(rounds)

    attempts_per_round = request.POST.get("attempts_per_round")
    if not validate_attempts_per_round(attempts_per_round):
        attempts_per_round = "3"
    attempts_per_round = int(attempts_per_round)

    abbrev_length = request.POST.get("abbrev_length")
    if not validate_abbrev_length(abbrev_length):
        abbrev_length = "3"
    abbrev_length = int(abbrev_length)

    abbrev = request.POST.get("abbrev")
    if not validate_abbrev(abbrev):
        abbrev = generate_abbrev(abbrev_length)
    else:
        abbrev_length = len(abbrev)

    user_guess = request.POST.get("guess")
    if not validate_guess(user_guess):
        user_guess = NO_REVABS_POSSIBLE

    guess_history = request.POST.get("guess_history")
    if not validate_guess_history(guess_history, attempts_per_round, abbrev):
        guess_history = json.dumps([{"number": i+1, "guess": EMPTY, "result": EMPTY, "score": EMPTY} for i in range(attempts_per_round)])
    guess_history = json.loads(guess_history.replace("\'", "\""))

    total_points = request.POST.get("total_points")
    if not validate_total_points(total_points):
        total_points = "0"
    total_points = int(total_points)

    opponent_round_history = request.POST.get("opponent_round_history")
    if validate_round_history(opponent_round_history):
        #if opponent round history is valid, that should set the number of rounds
        opponent_round_history = json.loads(opponent_round_history.replace("\'", "\""))
        rounds = len(opponent_round_history)

    round_history = request.POST.get("round_history")
    if not validate_round_history(round_history, rounds):
        round_history = json.dumps([{"number": i+1, "abbrev": EMPTY, "best_guess": EMPTY, "score": EMPTY} for i in range(rounds)])
        total_points = 0
    round_history = json.loads(round_history.replace("\'", "\""))

    round_number = 1
    for round in round_history:
        if round["abbrev"] == EMPTY:
            round_number = round["number"]
            break

    #start on final attempt
    attempt_number = attempts_per_round
    for guess in guess_history:
        #if no record of guess exists, then that attempt hasn't happened
        if guess["guess"] == EMPTY:
            attempt_number = guess["number"]
            break

    return {
        "rounds": rounds,
        "attempts_per_round": attempts_per_round,
        "abbrev_length": abbrev_length,
        "abbrev": abbrev,
        "user_guess": user_guess,
        "guess_history": guess_history,
        "total_points": total_points,
        "round_history": round_history,
        "opponent_round_history": opponent_round_history,
        "round_number": round_number,
        "attempt_number": attempt_number
    }

def best_guess(guess_history):
    best_score = -1
    best_guess = ""
    for guess in guess_history:
        if guess["score"] == EMPTY:
            continue
        if guess["score"] > best_score:
            best_score = guess["score"]
            best_guess = guess["guess"]
    return best_guess