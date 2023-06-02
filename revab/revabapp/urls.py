from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("settings", views.settings, name="settings"),
    path("help", views.help_page, name="help"),
    path("game", views.game, name="game"),
    path("stats", views.stats, name="stats"),
    path("challenge/start/<challenge_code>", views.start_challenge),
    path("challenge/name", views.get_name_for_challenge),
    path("challenge/link", views.display_challenge_link),
    path("challenge/game", views.challenge_game)
]