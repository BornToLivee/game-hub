from django.conf.urls.static import static
from django.urls import path

from game.views import index, GameListView, GenreListView, PublisherListView, register, personal_page, \
    update_wishlist_status, update_completed_status, game_detail, GameCreateView, GameUpdateView, GenreDetailView, \
    PublisherDetailView, about, RandomGameView, player_update, GenreCreateView, GenresUpdateView, GenreDeleteView, \
    PublisherCreateView, PublisherUpdateView, PublisherDeleteView, GameDeleteView
from game_hub import settings

urlpatterns = [
    path("", index, name="index"),
    path("games/", GameListView.as_view(), name="game-list"),
    path("games/<int:pk>/", game_detail, name="game-detail"),
    path("games/create/", GameCreateView.as_view(), name="game-create"),
    path("games/<int:pk>/update/",  GameUpdateView.as_view(), name="game-update"),
    path("games/<int:pk>/delete/", GameDeleteView.as_view(), name="game-delete"),
    path("genres/", GenreListView.as_view(), name="genre-list"),
    path("ganres/<int:pk>/", GenreDetailView.as_view(), name="genre-detail"),
    path("genres/create/", GenreCreateView.as_view(), name="genre-create"),
    path("genres/<int:pk>/update/", GenresUpdateView.as_view(), name="genre-update"),
    path("genres/<int:pk>/delete/", GenreDeleteView.as_view(), name="genre-delete"),
    path("publishers/", PublisherListView.as_view(), name="publisher-list"),
    path("publishers/<int:pk>/", PublisherDetailView.as_view(), name="publisher-detail"),
    path("publishers/create/", PublisherCreateView.as_view(), name="publisher-create"),
    path("publishers/<int:pk>/update/", PublisherUpdateView.as_view(), name="publisher-update"),
    path("publishers/<int:pk>/delete/", PublisherDeleteView.as_view(), name="publisher-delete"),
    path("register/", register, name="register"),
    path('update_wishlist_status/<int:game_id>/', update_wishlist_status, name='update-wishlist-status'),
    path('update_completed_status/<int:game_id>/', update_completed_status, name='update-completed-status'),
    path('personal_page/', personal_page, name='personal-page'),
    path('player/update/', player_update, name='player-update'),
    path('about/', about, name='about-page'),
    path('random/', RandomGameView.as_view(), name='random-game'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "game"