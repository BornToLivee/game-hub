from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Avg, Count
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    TemplateView,
)

from game.forms import (
    PlayerRegistrationForm,
    RatingForm,
    GameSearchForm,
    GameForm,
    PlayerUpdateForm,
    GenreCreateForm,
    PublisherCreateForm,
)
from game.models import Player, Game, Publisher, Genre, Rating


class IndexView(TemplateView):
    template_name = "game/index.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        context["num_players"] = Player.objects.count()
        context["num_games"] = Game.objects.count()
        context["num_publishers"] = Publisher.objects.count()
        context["num_genres"] = Genre.objects.count()
        return context


class RegistrationView(LoginRequiredMixin, CreateView):
    form_class = PlayerRegistrationForm
    template_name = "registration/register.html"
    success_url = reverse_lazy("game:personal-page")


class PlayerUpdateView(LoginRequiredMixin, UpdateView):
    model = Player
    form_class = PlayerUpdateForm
    template_name = "game/player_update.html"
    success_url = reverse_lazy("game:personal-page")

    def get_object(self):
        return self.request.user


def update_wishlist_status(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    player = request.user

    if game in player.wishlist_games.all():
        player.wishlist_games.remove(game)
    else:
        player.wishlist_games.add(game)
    return redirect("game:game-detail", pk=game_id)


def update_completed_status(request, game_id):
    game = get_object_or_404(Game, id=game_id)
    player = request.user

    if game in player.completed_games.all():
        player.completed_games.remove(game)
    else:
        player.completed_games.add(game)
    return redirect("game:game-detail", pk=game_id)


class PersonalPageView(LoginRequiredMixin, TemplateView):
    template_name = "game/personal_page.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        wishlist_games = self.request.user.wishlist_games.all()
        completed_games = self.request.user.completed_games.all()

        wishlist_paginator = Paginator(wishlist_games, 5)
        completed_paginator = Paginator(completed_games, 5)

        wishlist_page_number = self.request.GET.get("wishlist_page")
        completed_page_number = self.request.GET.get("completed_page")

        wishlist_page_obj = wishlist_paginator.get_page(wishlist_page_number)
        completed_page_obj = completed_paginator.get_page(completed_page_number)

        context.update(
            {
                "wishlist_games": wishlist_page_obj,
                "completed_games": completed_page_obj,
                "is_wishlist_paginated": wishlist_paginator.num_pages > 1,
                "is_completed_paginated": completed_paginator.num_pages > 1,
            }
        )

        return context


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


class GameCreateView(LoginRequiredMixin, CreateView):
    model = Game
    form_class = GameForm
    success_url = reverse_lazy("game:game-list")


class GameUpdateView(LoginRequiredMixin, UpdateView):
    model = Game
    form_class = GameForm

    def get_success_url(self):
        return reverse("game:game-detail", kwargs={"pk": self.object.pk})


class GameDeleteView(LoginRequiredMixin, DeleteView):
    model = Game
    success_url = reverse_lazy("game:game-list")


class GenreListView(ListView):
    model = Genre
    template_name = "game/genre_list.html"
    context_object_name = "genre_list"

    def get_queryset(self):
        queryset = Genre.objects.annotate(num_games=Count("game"))
        ordering = self.request.GET.get("ordering", "name")
        if ordering in ["num_games", "-num_games"]:
            queryset = queryset.order_by(ordering)
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["selected_ordering"] = self.request.GET.get("ordering", "name")
        context["genre_list"] = self.get_queryset()
        return context


class GenreDetailView(LoginRequiredMixin, DetailView):
    model = Genre

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        genre = self.object
        context["games"] = Game.objects.filter(genre_id=genre.pk)
        return context


class GenreCreateView(LoginRequiredMixin, CreateView):
    model = Genre
    form_class = GenreCreateForm
    template_name = "game/genre_create_form.html"
    success_url = reverse_lazy("game:genre-list")


class GenresUpdateView(LoginRequiredMixin, UpdateView):
    model = Genre
    form_class = GenreCreateForm
    template_name = "game/genre_create_form.html"

    def get_success_url(self):
        return reverse("game:genre-detail", kwargs={"pk": self.object.pk})


class GenreDeleteView(LoginRequiredMixin, DeleteView):
    model = Genre
    success_url = reverse_lazy("game:genre-list")


class PublisherListView(ListView):
    model = Publisher
    template_name = "game/publisher_list.html"
    context_object_name = "publisher_list"

    def get_queryset(self):
        queryset = super().get_queryset()
        selected_country = self.request.GET.get("country", "")
        selected_ordering = self.request.GET.get("ordering", "")

        if selected_country:
            queryset = queryset.filter(country=selected_country)

        if selected_ordering:
            queryset = queryset.order_by(selected_ordering)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["countries"] = Publisher.objects.values_list(
            "country", flat=True
        ).distinct()
        context["selected_country"] = self.request.GET.get("country", "")
        context["selected_ordering"] = self.request.GET.get("ordering", "")
        return context


class PublisherDetailView(LoginRequiredMixin, DetailView):
    model = Publisher

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        publisher = self.object
        context["games"] = Game.objects.filter(publisher_id=publisher.pk)
        return context


class GameDetailView(LoginRequiredMixin, DetailView):
    model = Game
    template_name = "game/game_detail.html"
    context_object_name = "game"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = self.get_object()
        average_rating = (
            Rating.objects.filter(game=game).aggregate(Avg("score"))["score__avg"] or 0
        )
        user_rating = None
        if self.request.user.is_authenticated:
            user_rating = Rating.objects.filter(
                game=game, player=self.request.user
            ).first()

        user_votes_count = (
            Rating.objects.filter(game=game).values("player").distinct().count()
        )
        range_list = range(11)
        context.update(
            {
                "average_rating": average_rating,
                "user_rating": user_rating,
                "form": RatingForm(),
                "range": range_list,
                "user_votes_count": user_votes_count,
            }
        )
        return context

    def post(self, request, *args, **kwargs):
        form = RatingForm(request.POST)
        game = self.get_object()
        if form.is_valid():
            rating, created = Rating.objects.update_or_create(
                player=request.user,
                game=game,
                defaults={"score": form.cleaned_data["score"]},
            )
            return redirect("game:game-detail", pk=game.pk)
        return self.get(request, *args, **kwargs)


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
    success_url = reverse_lazy("game:publisher-list")


class AboutView(TemplateView):
    template_name = "game/about.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["text"] = (
            "Hi, I'm the author of this cute little gaming site. My name is Bohdan, I'm 23 years old, and I'm a beginner Python developer. If you liked it and want to invite me to work, write to me by email. Thanks for stopping by, have a nice day!"
        )
        context["email"] = "bogdan.zinchenko.2019@gmail.com"
        context["github_account"] = "https://github.com/BornToLivee"
        return context


class RandomGameView(View):
    def get(self, request, *args, **kwargs):
        random_game = Game.objects.order_by("?").first()
        return redirect("game:game-detail", pk=random_game.pk)
