from django.contrib.auth import login
from django.db.models import Avg
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, DetailView, CreateView, UpdateView

from game.forms import PlayerRegistrationForm, RatingForm, GameSearchForm, GameForm
from game.models import Player, Game, Publisher, Genre, Rating


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
    paginate_by = 5
    queryset = Game.objects.select_related("genre", "publisher")

    def get_queryset(self):
        queryset = super().get_queryset()
        title = self.request.GET.get("title", "")
        genre_id = self.request.GET.get("genre")
        publisher_id = self.request.GET.get("publisher")

        if title:
            queryset = queryset.filter(title__icontains=title)
        if genre_id:
            queryset = queryset.filter(genre__id=genre_id)
        if publisher_id:
            queryset = queryset.filter(publisher__id=publisher_id)

        return queryset

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        title = self.request.GET.get("title", "")
        genre_id = self.request.GET.get("genre")
        publisher_id = self.request.GET.get("publisher")

        context["search_form"] = GameSearchForm(initial={"title": title})
        context["genres"] = Genre.objects.all()
        context["publishers"] = Publisher.objects.all()
        context["selected_genre"] = genre_id
        context["selected_publisher"] = publisher_id
        return context


class GameCreateView(CreateView):
    model = Game
    form_class = GameForm
    success_url = reverse_lazy("game:game-list")


class GameUpdateView(UpdateView):
    model = Game
    form_class = GameForm

    def get_success_url(self):
        return reverse("game:game-detail", kwargs={"pk": self.object.pk})


class GenreListView(ListView):
    model = Genre


class GenreDetailView(DetailView):
    model = Genre

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genre = self.object
        context['games'] = Game.objects.filter(genre_id=genre.pk)
        return context


class PublisherListView(ListView):
    model = Publisher
    paginate_by = 5


class PublisherDetailView(DetailView):
    model = Publisher

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publisher = self.object
        context['games'] = Game.objects.filter(publisher_id=publisher.pk)
        return context



def game_detail(request, pk):
    game = get_object_or_404(Game, pk=pk)
    average_rating = Rating.objects.filter(game=game).aggregate(Avg('score'))['score__avg'] or 0
    user_rating = None
    if request.user.is_authenticated:
        user_rating = Rating.objects.filter(game=game, player=request.user).first()

    range_list = range(1, 11)

    if request.method == "POST":
        form = RatingForm(request.POST)
        if form.is_valid():
            rating, created = Rating.objects.update_or_create(
                player=request.user,
                game=game,
                defaults={'score': form.cleaned_data['score']}
            )
            return redirect('game:game-detail', pk=pk)
    else:
        form = RatingForm()

    return render(request, 'game/game_detail.html', {
        'game': game,
        'average_rating': average_rating,
        'user_rating': user_rating,
        'form': form,
        'range': range_list,
    })