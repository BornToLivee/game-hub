from django.conf.urls.static import static
from django.urls import path

from game.views import index, GameListView, GenreListView, PublisherListView, GameDetailView, register
from game_hub import settings

urlpatterns = [
    path("", index, name="index"),
    path("games/", GameListView.as_view(), name="game-list"),
    path("games/<int:pk>/", GameDetailView.as_view(), name="game-detail"),
    path("genres/", GenreListView.as_view(), name="genre-list"),
    path("publishers/", PublisherListView.as_view(), name="publisher-list"),
    path("register/", register, name="register"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "game"