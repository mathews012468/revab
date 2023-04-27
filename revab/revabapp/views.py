from django.shortcuts import render
from django.http import HttpResponse
from revabapp.src.revab import generate_abbrev

# Create your views here.

def index(request):
    context = {}
    return render(request, "revabapp/index.html", context)

def game(request):
    #add input screening
    rounds = int(request.POST.get("rounds", 5))
    abbrev_length = int(request.POST.get("abbrev_length", 3))
    abbrev = generate_abbrev(abbrev_length)
    attempts_per_round = int(request.POST.get("attempts_per_round", 3))

    context = {
        "rounds": rounds,
        "abbrev": abbrev,
        "attempt_number": 1,
        "attempts_per_round": attempts_per_round,
        "total_points": 0,
        "round_history": [{"number": i+1, "abbrev": "...", "best_guess": "...", "score": "..."} for i in range(rounds)],
        "guess_history": [{"number": i+1, "guess": "...", "result": "...", "score": "..."} for i in range(attempts_per_round - 1)]
    }
    return render(request, "revabapp/game.html", context)