from django.conf.urls.static import static
from django.urls import path

from game import views
from game_hub import settings

urlpatterns = [
    path(
        "",
        views.IndexView.as_view(),
        name="index"
    ),
    path(
        "games/",
        views.GameListView.as_view(),
        name="game-list"
    ),
    path(
        "games/<int:pk>/",
        views.GameDetailView.as_view(),
        name="game-detail"
    ),
    path(
        "games/create/",
        views.GameCreateView.as_view(),
        name="game-create"
    ),
    path(
        "games/<int:pk>/update/",
        views.GameUpdateView.as_view(),
        name="game-update"
    ),
    path(
        "games/<int:pk>/delete/",
        views.GameDeleteView.as_view(),
        name="game-delete"
    ),
    path(
        "genres/",
        views.GenreListView.as_view(),
        name="genre-list"
    ),
    path(
        "ganres/<int:pk>/",
        views.GenreDetailView.as_view(),
        name="genre-detail"
    ),
    path(
        "genres/create/",
        views.GenreCreateView.as_view(),
        name="genre-create"
    ),
    path(
        "genres/<int:pk>/update/",
        views.GenresUpdateView.as_view(),
        name="genre-update"
    ),
    path(
        "genres/<int:pk>/delete/",
        views.GenreDeleteView.as_view(),
        name="genre-delete"
    ),
    path(
        "publishers/",
        views.PublisherListView.as_view(),
        name="publisher-list"
    ),
    path(
        "publishers/<int:pk>/",
        views.PublisherDetailView.as_view(),
        name="publisher-detail"
    ),
    path(
        "publishers/create/",
        views.PublisherCreateView.as_view(),
        name="publisher-create"
    ),
    path(
        "publishers/<int:pk>/update/",
        views.PublisherUpdateView.as_view(),
        name="publisher-update",
    ),
    path(
        "publishers/<int:pk>/delete/",
        views.PublisherDeleteView.as_view(),
        name="publisher-delete",
    ),
    path(
        "update_wishlist_status/<int:game_id>/",
        views.update_wishlist_status,
        name="update-wishlist-status",
    ),
    path(
        "update_completed_status/<int:game_id>/",
        views.update_completed_status,
        name="update-completed-status",
    ),
    path(
        "register/",
        views.RegistrationView.as_view(),
        name="register"
    ),
    path(
        "personal_page/",
        views.PersonalPageView.as_view(),
        name="personal-page"
    ),
    path(
        "player/update/",
        views.PlayerUpdateView.as_view(),
        name="player-update"
    ),
    path(
        "about/",
        views.AboutView.as_view(),
        name="about-page"
    ),
    path(
        "random/",
        views.RandomGameView.as_view(),
        name="random-game"
    ),
]


if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

app_name = "game"
