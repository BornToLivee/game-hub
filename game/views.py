from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect
from django.views.generic import ListView, DetailView

from game.forms import PlayerRegistrationForm
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


def register(request):
    if request.method == "POST":
        form = PlayerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")
    else:
        form = PlayerRegistrationForm()
    return render(request, "registration/register.html", {"form": form})


class GameListView(ListView):
    model = Game
    context_object_name = "game_list"
    template_name = "game/game_list.html"


class GenreListView(ListView):
    model = Genre
    context_object_name = "genre_list"
    template_name = "game/genre_list.html"


class PublisherListView(ListView):
    model = Publisher
    context_object_name = "publisher_list"
    template_name = "game/publisher_list.html"


class GameDetailView(DetailView):
    model = Game
    template_name = "game/game_detail.html"

