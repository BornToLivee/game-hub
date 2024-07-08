from django.contrib.auth import login
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
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


def update_wishlist_status(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    player = request.user

    if game in player.wishlist_games.all():
        player.wishlist_games.remove(game)
    else:
        player.wishlist_games.add(game)
    return redirect('game:game-detail', pk=game_id)


def update_completed_status(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    player = request.user

    if game in player.completed_games.all():
        player.completed_games.remove(game)
    else:
        player.completed_games.add(game)
    return redirect('game:game-detail', pk=game_id)


def personal_page(request):
    wishlist_games = request.user.wishlist_games.all()
    completed_games = request.user.completed_games.all()
    context = {
        'wishlist_games': wishlist_games,
        'completed_games': completed_games,
    }
    return render(request, 'game/personal_page.html', context)


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

