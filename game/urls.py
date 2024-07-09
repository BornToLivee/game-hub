from django.conf.urls.static import static
from django.urls import path

from game.views import index, GameListView, GenreListView, PublisherListView,register, personal_page, \
    update_wishlist_status, update_completed_status, game_detail
from game_hub import settings

urlpatterns = [
    path("", index, name="index"),
    path("games/", GameListView.as_view(), name="game-list"),
    path("games/<int:pk>/", game_detail, name="game-detail"),
    path("genres/", GenreListView.as_view(), name="genre-list"),
    path("publishers/", PublisherListView.as_view(), name="publisher-list"),
    path("register/", register, name="register"),
    path('update_wishlist_status/<int:game_id>/', update_wishlist_status, name='update-wishlist-status'),
    path('update_completed_status/<int:game_id>/', update_completed_status, name='update-completed-status'),
    path('personal_page/', personal_page, name='personal-page'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = "game"