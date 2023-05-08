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
    validate_abbrev_length, \
    validate_abbrev, \
    validate_guess, \
    validate_total_points
import re
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
    context = reasonable_defaults(request)
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

def game(request):
    context = reasonable_defaults(request)

    #if we come from the help page, just load the page, don't do any computations
    if request.POST.get("source") in {"help", "home", "results"}:
        return render(request, "revabapp/game.html", context)

    #submit user guess
    words = load_words()
    guess_type = request.POST.get('submitbutton')
    if guess_type != "Guess":
        context["user_guess"] = "."
    outcome, score = check_user_guess(context["abbrev"], context["user_guess"], words)
    
    #calculate score
    round_score = 0
    for guess in context["guess_history"]:
        if guess["score"] == "...":
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
        context["guess_history"] = [{"number": i+1, "guess": "...", "result": "...", "score": "..."} for i in range(context["attempts_per_round"])]
        context["round_number"] += 1

    #if game is over, move to results page
    if context["round_number"] > context["rounds"]:
        return render(request, "revabapp/results.html", context)

    #else, stay on the game page
    return render(request, "revabapp/game.html", context)

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
        user_guess = "."

    guess_history = request.POST.get("guess_history")
    if not validate_guess_history(guess_history, attempts_per_round, abbrev):
        guess_history = json.dumps([{"number": i+1, "guess": "...", "result": "...", "score": "..."} for i in range(attempts_per_round)])
    guess_history = json.loads(guess_history.replace("\'", "\""))

    total_points = request.POST.get("total_points")
    if not validate_total_points(total_points):
        total_points = "0"
    total_points = int(total_points)

    round_history = request.POST.get("round_history")
    if not validate_round_history(round_history, rounds):
        round_history = json.dumps([{"number": i+1, "abbrev": "...", "best_guess": "...", "score": "..."} for i in range(rounds)])
        total_points = 0
    round_history = json.loads(round_history.replace("\'", "\""))

    round_number = 1
    for round in round_history:
        if round["abbrev"] == "...":
            round_number = round["number"]
            break

    #start on final attempt
    attempt_number = attempts_per_round
    for guess in guess_history:
        #if no record of guess exists, then that attempt hasn't happened
        if guess["guess"] == "...":
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
        "round_number": round_number,
        "attempt_number": attempt_number
    }

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