from django.contrib.auth import get_user_model
from django.test import TestCase

from game.models import (
    Game,
    Genre,
    Publisher,
    Platform
)


class ModelsStrTestCase(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name="Action", description="Action games")
        self.publisher = Publisher.objects.create(
            name="Test Publisher",
            description="Test Publisher",
            country="USA",
            capitalization=0.01,
        )
        self.platform = Platform.objects.create(name="Test Platform")
        self.player = get_user_model().objects.create_user(
            username="player", password="password"
        )
        self.image = "test_image.jpg"

        self.game = Game.objects.create(
            title="Game 1",
            description="Description of Game 1",
            release_year=2023,
            genre=self.genre,
            publisher=self.publisher,
            image=self.image,
            link="https://example.com/game1",
        )
        self.game.platform.set([self.platform])
        self.game.players.add(self.player)

    def test_game_str(self):
        self.assertEqual(str(self.game), "Game 1")

    def test_genre_str(self):
        self.assertEqual(str(self.genre), "Action")

    def test_publisher_str(self):
        self.assertEqual(str(self.publisher), "Test Publisher")

    def test_platform_str(self):
        self.assertEqual(str(self.platform), "Test Platform")

    def test_player_str(self):
        self.assertEqual(str(self.player), "player")
