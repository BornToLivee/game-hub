from unittest.mock import MagicMock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.test import (
    Client,
    RequestFactory,
    TestCase,
)
from django.urls import reverse

from game.models import (
    Genre,
    Platform,
    Player,
    Publisher,
)
from game.views import PersonalPageView, PlayerUpdateView


class PlayerUpdateViewTestCase(TestCase):
    def test_registration_form_renders_correctly(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("game:register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "registration/register.html")

    def test_user_can_successfully_submit_registration_form(self):
        client = Client()
        response = client.post(
            reverse("game:register"),
            {
                "username": "test_user_1",
                "password1": "testpassword123tttttyy",
                "password2": "testpassword123tttttyy",
            },
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("game:personal-page"))

    def test_form_submission_with_already_taken_username(self):
        Player.objects.create_user(username="test_user", password="test_password")
        form_data = {
            "username": "test_user",
            "email": "test@example.com",
            "date_of_birth": "2000-01-01",
            "first_name": "Test",
            "last_name": "User",
            "password1": "test_password3124",
            "password2": "test_password3124",
        }

        response = self.client.post(reverse("game:register"), form_data)
        self.assertFalse(response.context["form"].is_valid())


class PlayerUpdateViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = Player.objects.create_user(
            username="testuser1", password="12345", email="testuser@example.com"
        )
        self.client.login(username="testuser1", password="12345")

    def test_successful_update(self):
        response = self.client.post(
            reverse("game:player-update"),
            {"first_name": "John", "last_name": "Doe", "date_of_birth": "1990-01-01"},
        )
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, "John")
        self.assertEqual(self.user.last_name, "Doe")
        self.assertEqual(str(self.user.date_of_birth), "1990-01-01")

    def test_redirects_on_success(self):
        factory = RequestFactory()
        request = factory.post(
            "/player/update/",
            {"first_name": "John", "last_name": "Doe", "date_of_birth": "1990-01-01"},
        )
        request.user = Player.objects.create_user(username="testuser", password="12345")

        view = PlayerUpdateView()
        view.setup(request)
        response = view.post(request)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, "/personal_page/")

    def test_player_update_view_with_current_user_data(self):
        client = self.client
        player = get_user_model().objects.create_user(
            username="testuser", password="12345"
        )
        client.login(username="testuser", password="12345")
        response = client.get(reverse("game:player-update"))
        self.assertContains(response, player.username)

    def test_correct_template_rendering(self):
        response = self.client.get(reverse("game:player-update"))
        self.assertTemplateUsed(response, "game/player_update.html")


class PersonalPageViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username="test_user", password="12345"
        )
        self.client.login(username="test_user", password="12345")

        self.genre = Genre.objects.create(name="Test Genre", description="Test Genre")
        self.platform = Platform.objects.create(name="Test Platform")
        self.publisher = Publisher.objects.create(
            name="Test Publisher",
            description="Test Publisher",
            country="Ukraine",
            capitalization=0.02,
        )

    def test_user_with_wishlist_and_completed_games_sees_paginated_lists(self):
        user = User(username="testuser")
        user.wishlist_games = MagicMock()
        user.completed_games = MagicMock()
        user.wishlist_games.all.return_value = [
            "game1",
            "game2",
            "game3",
            "game4",
            "game5",
            "game6",
        ]
        user.completed_games.all.return_value = [
            "game1",
            "game2",
            "game3",
            "game4",
            "game5",
            "game6",
        ]

        request = RequestFactory().get("/personal_page")
        request.user = user

        view = PersonalPageView()
        view.setup(request)

        context = view.get_context_data()

        self.assertIn("wishlist_games", context)
        self.assertIn("completed_games", context)

    def test_user_without_wishlist_or_completed_games_sees_empty_lists(self):
        user = User(username="testuser")
        user.wishlist_games = MagicMock()
        user.completed_games = MagicMock()
        user.wishlist_games.all.return_value = []
        user.completed_games.all.return_value = []

        request = RequestFactory().get("/personal_page")
        request.user = user

        view = PersonalPageView()
        view.setup(request)

        context = view.get_context_data()

        self.assertEqual(len(context["wishlist_games"]), 0)
        self.assertEqual(len(context["completed_games"]), 0)

    def test_user_requests_non_existent_wishlist_page_number(self):
        user = User(username="testuser")
        user.wishlist_games = MagicMock()
        user.completed_games = MagicMock()
        user.wishlist_games.all.return_value = ["game1", "game2", "game3"]
        user.completed_games.all.return_value = ["game1", "game2", "game3"]

        request = RequestFactory().get("/personal_page", {"wishlist_page": 999})
        request.user = user

        view = PersonalPageView()
        view.setup(request)

        context = view.get_context_data()

        self.assertEqual(context["wishlist_games"].number, 1)

    def test_correct_template_rendered(self):
        response = self.client.get(reverse("game:personal-page"))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/personal_page.html")

    def test_pagination_completed_games(self):
        request = RequestFactory().get("/personal_page/?completed_page=2")
        request.user = self.user

        view = PersonalPageView()
        view.request = request

        context = view.get_context_data()

        self.assertTrue("completed_games" in context)
        self.assertTrue("is_completed_paginated" in context)

    def test_pagination_wishlist_games(self):
        request = RequestFactory().get("/personal_page/?wishlist_page=2")
        request.user = self.user

        view = PersonalPageView()
        view.request = request

        context = view.get_context_data()

        self.assertTrue("wishlist_games" in context)
        self.assertTrue("is_wishlist_paginated" in context)
