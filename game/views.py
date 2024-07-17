from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
import json
from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView

from game.forms import PlayerRegistrationForm, RatingForm, GameSearchForm, GameForm, PlayerUpdateForm, GenreCreateForm, \
    PublisherCreateForm
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


def player_update(request):
    if request.method == 'POST':
        form = PlayerUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('game:personal-page')
    else:
        form = PlayerUpdateForm(instance=request.user)
    return render(request, 'game/player_update.html', {'form': form})


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

    wishlist_paginator = Paginator(wishlist_games, 5)  # 5 игр на страницу
    completed_paginator = Paginator(completed_games, 5)

    wishlist_page_number = request.GET.get('wishlist_page')
    completed_page_number = request.GET.get('completed_page')

    wishlist_page_obj = wishlist_paginator.get_page(wishlist_page_number)
    completed_page_obj = completed_paginator.get_page(completed_page_number)

    context = {
        'wishlist_games': wishlist_page_obj,
        'completed_games': completed_page_obj,
        'is_wishlist_paginated': wishlist_paginator.num_pages > 1,
        'is_completed_paginated': completed_paginator.num_pages > 1,
    }

    return render(request, 'game/personal_page.html', context)


class GameListView(ListView):
    model = Game
    paginate_by = 6
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


class GameDeleteView(DeleteView):
    model = Game
    success_url = reverse_lazy("game:game-list")


class GenreListView(ListView):
    model = Genre


class GenreDetailView(DetailView):
    model = Genre

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genre = self.object
        context['games'] = Game.objects.filter(genre_id=genre.pk)
        return context


class GenreCreateView(CreateView):
    model = Genre
    form_class = GenreCreateForm
    template_name = "game/genre_create_form.html"
    success_url = reverse_lazy("game:genre-list")


class GenresUpdateView(UpdateView):
    model = Genre
    form_class = GenreCreateForm
    template_name = "game/genre_create_form.html"

    def get_success_url(self):
        return reverse("game:genre-detail", kwargs={"pk": self.object.pk})


class GenreDeleteView(DeleteView):
    model = Genre
    success_url = reverse_lazy("game:genre-list")


class PublisherListView(ListView):
    model = Publisher
    template_name = 'game/publisher_list.html'
    context_object_name = 'publisher_list'
    paginate_by = 9

    def get_queryset(self):
        queryset = super().get_queryset()
        country = self.request.GET.get('country')

        if country:
            queryset = queryset.filter(country=country)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        countries = Publisher.objects.values_list('country', flat=True)
        unique_countries = list(set(countries))
        unique_countries.sort()

        context['countries'] = unique_countries
        context['selected_country'] = self.request.GET.get('country', '')

        return context

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

    user_votes_count = Rating.objects.filter(game=game).values('player').distinct().count()

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
        "user_votes_count": user_votes_count,
    })


class PublisherCreateView(CreateView):
    model = Publisher
    form_class = PublisherCreateForm
    template_name = "game/publisher_create_form.html"
    success_url = reverse_lazy("game:publisher-list")


class PublisherUpdateView(UpdateView):
    model = Publisher
    form_class = PublisherCreateForm
    template_name = "game/publisher_create_form.html"

    def get_success_url(self):
        return reverse("game:publisher-detail", kwargs={"pk": self.object.pk})


class PublisherDeleteView(DeleteView):
    model = Publisher
    success_url = reverse_lazy("game:publisher-list.html")


def about(request: HttpRequest) -> HttpResponse:
    text = "Hi, I'm the author of this cute little gaming site. My name is Bohdan, I'm 23 years old, and I'm a beginner Python developer. If you liked it and want to invite me to work, write to me by email. Thanks for stopping by, have a nice day!"
    email = "bogdan.zinchenko.2019@gmail.com"
    github_account = "https://github.com/BornToLivee"
    return render(request, "game/about.html", {
        'text': text,
        'email': email,
        'github_account': github_account
    })


class RandomGameView(View):
    def get(self, request, *args, **kwargs):
        random_game = Game.objects.order_by('?').first()
        return redirect('game:game-detail', pk=random_game.pk)


