from django.shortcuts import render
from django.http import HttpResponse
from revabapp.src.revab import \
    generate_abbrev, \
    check_user_guess, \
    load_words, \
    GuessOutcome
from revabapp.src.validate import \
    validate_round_history, \
    validate_guess_history, \
    validate_rounds, \
    validate_attempts_per_round, \
    validate_abbrev_length
import re
import json

# Create your views here.

def index(request):
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

    save_or_clear = request.POST.get("settings", "default")
    if "default" in save_or_clear:
        abbrev_length = 3
        attempts_per_round = 3
        rounds = 5

    context = {
        "rounds": rounds,
        "attempts_per_round": attempts_per_round,
        "abbrev_length": abbrev_length
    }
    return render(request, "revabapp/index.html", context)

def settings(request):
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
    
    context = {
        "rounds": rounds,
        "attempts_per_round": attempts_per_round,
        "abbrev_length": abbrev_length
    }
    return render(request, "revabapp/settings.html", context)

def help_page(request):
    context = {
        "rounds": request.POST.get('rounds'),
        "attempts_per_round": request.POST.get('attempts_per_round'),
        "abbrev_length": request.POST.get('abbrev_length'),
        "abbrev": request.POST.get('abbrev'),
        "guess_history": request.POST.get('guess_history'),
        "round_history": request.POST.get('round_history'),
        "total_points": request.POST.get('total_points'),
        "settings": request.POST.get('settings'),
        "destination": request.POST.get('destination')
    }

    return render(request, "revabapp/help.html", context)

def best_guess(guess_history):
    best_score = -1
    best_guess = ""
    for guess in guess_history:
        if guess["score"] == "...":
            continue
        if guess["score"] > best_score:
            best_score = guess["score"]
            best_guess = guess["guess"]
    return best_guess

def game(request):
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

    #if abbrev doesn't exist or isn't three or four letters, restart game
    abbrev_pattern = r'^[a-zA-Z]{3,4}$'
    abbrev = request.POST.get("abbrev")
    if abbrev is None or not re.match(abbrev_pattern, abbrev):
        abbrev = generate_abbrev(abbrev_length)

    guess_pattern = r'^[a-zA-Z]{1,25}$'
    user_guess = request.POST.get("guess")
    if user_guess is None or not re.match(guess_pattern, user_guess):
        user_guess = "."

    guess_history = request.POST.get("guess_history", "[]")
    guess_history = guess_history.replace("\'", "\"")
    try:
        guess_history = json.loads(guess_history)
    except json.JSONDecodeError:
        guess_history = [{"number": i+1, "guess": "...", "result": "...", "score": "..."} for i in range(attempts_per_round)]
    if not validate_guess_history(guess_history, attempts_per_round, abbrev):
        guess_history = [{"number": i+1, "guess": "...", "result": "...", "score": "..."} for i in range(attempts_per_round)]

    total_points_pattern = r'^\d{1,3}$'
    total_points = request.POST.get("total_points", "0")
    if not re.match(total_points_pattern, total_points):
        total_points = "0"
    total_points = int(total_points)

    round_history = request.POST.get("round_history", "[]")
    round_history = round_history.replace("\'", "\"")
    try:
        round_history = json.loads(round_history)
    except json.JSONDecodeError:
        round_history = [{"number": i+1, "abbrev": "...", "best_guess": "...", "score": "..."} for i in range(rounds)]
        total_points = 0
    if not validate_round_history(round_history, rounds):
        round_history = [{"number": i+1, "abbrev": "...", "best_guess": "...", "score": "..."} for i in range(rounds)]
        total_points = 0

    round_number = 1
    for round in round_history:
        if round["abbrev"] == "...":
            round_number = round["number"]
            break

    #if we come from the help page, just load the page, don't do any computations
    if request.POST.get("source") in {"help", "home", "results"}:
        context = {
            "rounds": rounds,
            "abbrev": abbrev,
            "round_number": round_number,
            "attempts_per_round": attempts_per_round,
            "total_points": total_points,
            "round_history": round_history,
            "guess_history": guess_history
        }
        return render(request, "revabapp/game.html", context)

    #start on final attempt
    attempt_number = attempts_per_round
    for guess in guess_history:
        #if no record of guess exists, then that attempt hasn't happened
        if guess["guess"] == "...":
            attempt_number = guess["number"]
            break

    words = load_words()
    guess_type = request.POST.get('submitbutton')
    if guess_type == "Guess":
        outcome, score = check_user_guess(abbrev, user_guess, words)
    else:
        outcome, score = check_user_guess(abbrev, ".", words)
    
    round_score = 0
    for guess in guess_history:
        if guess["score"] == "...":
            break
        if guess["score"] > round_score:
            round_score = guess["score"]
    round_score = max(round_score, score)
    
    if outcome == GuessOutcome.BEST_WORD or outcome == GuessOutcome.NONE_IS_CORRECT:
        #this is my signal that the round is over later on
        attempt_number = attempts_per_round
    guess_history[attempt_number - 1] = {"number": attempt_number, "guess": user_guess, "result": outcome.value, "score": score}

    if attempt_number == attempts_per_round:
        #update round history
        #generate abbrev
        #update total points
        #reset guess history
        #update round number
        round_history[round_number - 1] = {"number": round_number, "abbrev": abbrev, "best_guess": best_guess(guess_history), "score": round_score}
        abbrev = generate_abbrev(abbrev_length)
        total_points += round_score
        guess_history = [{"number": i+1, "guess": "...", "result": "...", "score": "..."} for i in range(attempts_per_round)]
        round_number += 1

    #if game is over, move to results page
    if round_number > rounds:
        context = {
            "rounds": rounds,
            "attempts_per_round": attempts_per_round,
            "abbrev_length": abbrev_length,
            "total_points": total_points,
            "round_history": round_history,
        }
        return render(request, "revabapp/results.html", context)

    context = {
        "rounds": rounds,
        "abbrev": abbrev,
        "round_number": round_number,
        "attempts_per_round": attempts_per_round,
        "total_points": total_points,
        "round_history": round_history,
        "guess_history": guess_history
    }
    return render(request, "revabapp/game.html", context)