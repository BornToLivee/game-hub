import os
import shutil
import tempfile
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase, Client, RequestFactory
from django.urls import reverse
from game.models import Game, Genre, Platform, Publisher, Player, Rating


class GameListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.genre = Genre.objects.create(name="Action", description="Action games")
        self.platform = Platform.objects.create(name="PC")
        self.publisher = Publisher.objects.create(name="Epic Games", description="Epic Games Publisher", country="USA", capitalization=Decimal("10.00"))
        for i in range(10):
            Game.objects.create(
                title=f"Test Game {i + 1}",
                description=f"Description for Test Game {i + 1}",
                release_year=2023,
                genre=self.genre,
                publisher=self.publisher,
                link=f"https://www.testgame{i + 1}.com",
                image="image.jpg"
            )

    def test_retrieve_games_with_pagination(self):
        response = self.client.get(reverse('game:game-list') + '?page=2')
        self.assertEqual(response.status_code, 200)
        self.assertIn('page_obj', response.context)
        page_obj = response.context['page_obj']
        self.assertEqual(len(page_obj.object_list), 4)
        self.assertEqual(page_obj.number, 2)

    def test_filter_games_by_title(self):
        Game.objects.create(
            title="Test Game",
            description="Description for Test Game",
            release_year=2023,
            genre=self.genre,
            publisher=self.publisher,
            link="https://www.testgame.com",
            image="test_image.jpg"
        )
        response = self.client.get(reverse('game:game-list') + '?title=Test Game')
        self.assertEqual(response.status_code, 200)
        self.assertIn('object_list', response.context)
        self.assertEqual(len(response.context['object_list']), 6)
        self.assertEqual(response.context['object_list'][0].title, "Test Game")

    def test_display_all_genres(self):
        self.genre1 = Genre.objects.create(name="Horror", description="Horror games")
        self.genre2 = Genre.objects.create(name="Adventure", description="Adventure games")
        self.genre3 = Genre.objects.create(name="Strategy", description="Strategy games")
        response = self.client.get(reverse('game:game-list'))

        self.assertIn('genres', response.context)
        genres_in_context = response.context['genres']
        self.assertIn(self.genre1, genres_in_context)
        self.assertIn(self.genre2, genres_in_context)
        self.assertIn(self.genre3, genres_in_context)


class GameCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='sadfawsfsdaf')
        self.client.login(username='testuser', password='sadfawsfsdaf')

        self.genre = Genre.objects.create(name='Action', description='Action games')
        self.publisher = Publisher.objects.create(name='Test Publisher', description='Test Publisher desc', country="USA",
                                                  capitalization=0.02)
        self.platform = Platform.objects.create(name='Test Platform')

        self.image = "image.jpg"
        self.create_url = reverse('game:game-create')

    def test_create_game_view_unauthenticated(self):
        self.client.logout()
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={self.create_url}')


class GameDeleteViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.genre = Genre.objects.create(name="Action", description="Action games")
        self.platform = Platform.objects.create(name="PC")
        self.publisher = Publisher.objects.create(
            name="Epic Games",
            description="Epic Games Publisher",
            country="USA",
            capitalization=Decimal("10.00")
        )
        self.game = Game.objects.create(
            title="Test Game",
            description="Description for Test Game",
            release_year=2023,
            genre=self.genre,
            publisher=self.publisher,
            link="https://www.testgame.com",
            image="image.jpeg"
        )
        self.game.platform.set([self.platform])
        self.game.save()

    def test_successful_deletion_logged_in_user(self):
        self.client.login(username='testuser', password='12345')
        response = self.client.post(reverse('game:game-delete', kwargs={'pk': self.game.pk}))

        self.assertEqual(response.status_code, 302)
        self.assertFalse(Game.objects.filter(pk=self.game.pk).exists())
        self.assertRedirects(response, reverse('game:game-list'))

    def test_confirmation_prompt_displayed(self):
        self.client.login(username='testuser', password='12345')
        url = reverse("game:game-delete", kwargs={"pk": self.game.pk})
        response = self.client.get(url)
        self.assertContains(response, "Are you sure you want to delete")


class GameDetailViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.factory = RequestFactory()
        self.user = get_user_model().objects.create_user(username='testuser', password='12345', email="qwe@qwe.com")
        self.genre = Genre.objects.create(name="Action", description="Action games")
        self.platform = Platform.objects.create(name="PC")
        self.publisher = Publisher.objects.create(
            name="Epic Games",
            description="Epic Games Publisher",
            country="USA",
            capitalization=Decimal("10.00")
        )
        self.game = Game.objects.create(
            title="Test Game",
            description="Description for Test Game",
            release_year=2023,
            genre=self.genre,
            publisher=self.publisher,
            link="https://www.testgame.com",
            image="image.jpeg"
        )
        self.game.platform.set([self.platform])
        self.game.save()

    def test_renders_game_detail_for_authenticated_users(self):
        self.client.login(username='testuser', password='12345')

        url = reverse('game:game-detail', kwargs={'pk': self.game.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.game.title)
        self.assertContains(response, self.game.description)
        self.assertContains(response, self.game.release_year)
        self.assertContains(response, self.game.link)
        self.assertContains(response, self.game.image.url)
        self.assertContains(response, "Average players rating")

    def test_calculate_unique_user_votes(self):
        player1 = Player.objects.create(username="player1", password="<PASSWORD>")
        player2 = Player.objects.create(username="player2", password="<PASSWORD>")
        Rating.objects.create(player=player1, game=self.game, score=8)
        Rating.objects.create(player=player2, game=self.game, score=6)
        self.client.force_login(player1)
        response = self.client.get(reverse("game:game-detail", kwargs={"pk": self.game.pk}))
        self.assertEqual(response.context["user_votes_count"], 2)

