import shutil
import tempfile
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpRequest
from django.test import TestCase, Client
from django.urls import reverse, reverse_lazy
from django.views.generic import DetailView
from game.models import Genre, Publisher, Game
from game.views import GenreListView, GenreDetailView, GenreDeleteView, GenresUpdateView
from game_hub import settings


class GenreListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.media_root = tempfile.mkdtemp()
        settings.MEDIA_ROOT = self.media_root

    def tearDown(self):
        shutil.rmtree(self.media_root, ignore_errors=True)

    def test_renders_correct_template(self):
        response = self.client.get(reverse('game:genre-list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/genre_list.html")

    def test_queryset_annotated_with_num_games(self):
        Genre.objects.create(name="Action", description="Action games")
        request = HttpRequest()
        view = GenreListView()
        view.request = request
        queryset = view.get_queryset()
        self.assertTrue(hasattr(queryset.first(), 'num_games'))

    def test_handles_empty_queryset(self):
        response = self.client.get(reverse('game:genre-list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "There are no genres in the hub")

    def test_handles_missing_image_fields(self):
        genre = Genre.objects.create(name="Test Genre", description="Test Description")
        response = self.client.get(reverse('game:genre-list'))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn(genre, context["genre_list"])


class GenreDetailViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='12345', email="qwe@qwe.com")
        self.client.login(username='testuser', password='12345')
        self.genre = Genre.objects.create(
            name="Action",
            description="Action games2",
        )

    def test_genre_detail_view_returns_correct_context_data(self):
        publisher = Publisher.objects.create(name="Test Publisher")
        game = Game.objects.create(
            title="Game 1",
            description="Description 1",
            release_year=2020,
            genre=self.genre,
            publisher=publisher,
            link="http://example.com"
        )

        response = self.client.get(reverse('game:genre-detail', kwargs={'pk': self.genre.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('games', response.context_data)
        self.assertEqual(list(response.context_data['games']), [game])

    def test_genre_detail_view_handles_no_associated_games(self):
        genre = Genre.objects.create(name="Puzzle", description="Puzzle games")
        response = self.client.get(reverse('game:genre-detail', kwargs={'pk': genre.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertIn('games', response.context_data)
        self.assertEqual(list(response.context_data['games']), [])

    def test_inheritance(self):
        self.assertTrue(issubclass(GenreDetailView, LoginRequiredMixin))
        self.assertTrue(issubclass(GenreDetailView, DetailView))

    def test_genre_detail_view_contains_update_and_delete_links(self):
        response = self.client.get(reverse('game:genre-detail', kwargs={'pk': self.genre.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, reverse('game:genre-update', kwargs={'pk': self.genre.pk}))
        self.assertContains(response, reverse('game:genre-delete', kwargs={'pk': self.genre.pk}))


class GenreDeleteViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_delete_genre_authenticated_and_redirected_correctly(self):
        genre = Genre.objects.create(name='Test Genre', description='Test Description')
        response = self.client.post(reverse('game:genre-delete', kwargs={'pk': genre.id}))
        self.assertRedirects(response, reverse('game:genre-list'))
        self.assertFalse(Genre.objects.filter(id=genre.id).exists())
        self.assertEqual(response.status_code, 302)

    def test_success_url_set_to_genre_list_page(self):
        genre_delete_view = GenreDeleteView()
        self.assertEqual(genre_delete_view.success_url, reverse_lazy("game:genre-list"))


class GenresUpdateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        self.genre = Genre.objects.create(
            name='Original Genre',
            description='Original Description',
        )

    def test_update_view_uses_correct_template(self):
        response = self.client.get(reverse('game:genre-update', kwargs={'pk': self.genre.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/genre_create_form.html")

    def test_successful_update(self):
        updated_data = {
            'name': 'Updated Genre',
            'description': 'Updated Description',
        }
        response = self.client.post(reverse('game:genre-update', kwargs={'pk': self.genre.pk}), data=updated_data)
        self.genre.refresh_from_db()
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('game:genre-detail', kwargs={'pk': self.genre.pk}))
        self.assertEqual(self.genre.name, 'Updated Genre')
        self.assertEqual(self.genre.description, 'Updated Description')

    def test_update_view_non_existent_genre(self):
        response = self.client.get(reverse('game:genre-update', kwargs={'pk': 999}))
        self.assertEqual(response.status_code, 404)


class GenreCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.url = reverse('game:genre-create')

    def test_create_genre_with_valid_data(self):
        valid_data = {
            'name': 'Adventure',
            'description': 'Adventure games'
        }
        response = self.client.post(self.url, data=valid_data)
        self.assertRedirects(response, reverse('game:genre-list'))
        self.assertTrue(Genre.objects.filter(name='Adventure').exists())

    def test_create_genre_with_invalid_data(self):
        invalid_data = {
            'name': '',
            'description': 'Adventure games'
        }
        response = self.client.post(self.url, data=invalid_data)
        self.assertEqual(response.status_code, 200)
        form = response.context.get('form')
        self.assertIsNotNone(form)
        self.assertTrue(form.errors)
        self.assertIn('name', form.errors)
        self.assertEqual(form.errors['name'], ['This field is required.'])

    def test_redirect_if_not_logged_in(self):
        self.client.logout()
        response = self.client.get(self.url)
        self.assertRedirects(response, f'/accounts/login/?next={self.url}')

    def test_correct_template_used(self):
        response = self.client.get(self.url)
        self.assertTemplateUsed(response, 'game/genre_create_form.html')