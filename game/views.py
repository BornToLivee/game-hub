from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from game.models import Player, Game, Publisher, Genre


def index(request: HttpRequest) -> HttpResponse:
    """View function for the home page of the site."""

    num_players = Player.objects.count()
    num_games = Game.objects.count()
    num_publishers = Publisher.objects.count()
    num_genres = Genre.objects.count()

    num_visits = request.session.get("num_visits", 0)
    request.session["num_visits"] = num_visits + 1

    context = {
        "num_players": num_players,
        "num_games": num_games,
        "num_publishers": num_publishers,
        "num_genres": num_genres,
        "num_visits": num_visits + 1,
    }

    return render(request, "game/index.html", context=context)
