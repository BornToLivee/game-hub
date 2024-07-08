from django.conf.urls.static import static
from django.urls import path

from game.views import index, GameListView, GenreListView, PublisherListView
from game_hub import settings

urlpatterns = [
    path("", index, name="index"),
    path("games/", GameListView.as_view(), name="game-list"),
    path("genres/", GenreListView.as_view(), name="genre-list"),
    path("publishers/", PublisherListView.as_view(), name="publisher-list"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "game"