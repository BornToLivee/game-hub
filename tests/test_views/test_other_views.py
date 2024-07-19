from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from game.models import (
    Game,
    Genre,
    Publisher,
    Platform,
    Player
)


class IndexViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser", password="12345"
        )
        self.client.login(username="testuser", password="12345")

        self.player1 = Player.objects.create(username="player1", password="password")
        self.player2 = Player.objects.create(username="player2", password="password")

        self.genre = Genre.objects.create(name="Action", description="Action games")
        self.publisher = Publisher.objects.create(
            name="Test Publisher",
            description="Test Publisher",
            country="USA",
            capitalization=0.01,
        )

        self.game1 = Game.objects.create(
            title="Game 1",
            description="Description 1",
            release_year=2021,
            genre=self.genre,
            publisher=self.publisher,
            link="https://example.com/game1",
        )
        self.game2 = Game.objects.create(
            title="Game 2",
            description="Description 2",
            release_year=2022,
            genre=self.genre,
            publisher=self.publisher,
            link="https://example.com/game2",
        )

        self.url = reverse("game:index")

    def test_index_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_index_view_uses_correct_template(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "game/index.html")

    def test_index_view_context_data(self):
        response = self.client.get(self.url)
        context = response.context_data

        self.assertEqual(context["num_players"], Player.objects.count())
        self.assertEqual(context["num_games"], Game.objects.count())
        self.assertEqual(context["num_publishers"], Publisher.objects.count())
        self.assertEqual(context["num_genres"], Genre.objects.count())


class AboutViewTestCase(TestCase):
    def setUp(self):
        self.url = reverse("game:about-page")

    def test_about_view_status_code(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_about_view_contains_expected_context(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

        self.assertIn("text", response.context)
        self.assertIn("email", response.context)
        self.assertIn("github_account", response.context)

    def test_about_view_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, "game/about.html")


class RandomGameViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="testuser", password="12345"
        )
        self.client.login(username="testuser", password="12345")

        self.genre = Genre.objects.create(name="Test Genre", description="Test Genre")
        self.publisher = Publisher.objects.create(
            name="Test Publisher",
            description="Test Publisher",
            country="Ukraine",
            capitalization=0.02,
        )
        self.platform1 = Platform.objects.create(name="Test Platform 1")
        self.platform2 = Platform.objects.create(name="Test Platform 2")

        self.game1 = Game.objects.create(
            title="Game 1",
            description="Description 1",
            release_year=2021,
            genre=self.genre,
            publisher=self.publisher,
            link="https://example.com/game1",
        )
        self.game1.platform.add(self.platform1)

        self.game2 = Game.objects.create(
            title="Game 2",
            description="Description 2",
            release_year=2022,
            genre=self.genre,
            publisher=self.publisher,
            link="https://example.com/game2",
        )
        self.game2.platform.add(self.platform1, self.platform2)

        self.random_game_url = reverse("game:random-game")

    def test_random_game_redirects_to_game_detail(self):
        response = self.client.get(self.random_game_url)
        self.assertEqual(response.status_code, 302)

        redirected_url = response["Location"]
        game_detail_url = reverse("game:game-detail", kwargs={"pk": self.game1.pk})

        self.assertTrue(
            redirected_url.endswith(game_detail_url)
            or redirected_url.endswith(
                reverse("game:game-detail", kwargs={"pk": self.game2.pk})
            )
        )
