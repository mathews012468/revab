from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("settings", views.settings, name="settings"),
    path("help", views.help_page, name="help"),
    path("game", views.game, name="game"),
]