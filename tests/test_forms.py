from datetime import timedelta, date
from decimal import Decimal
from django.utils import timezone

from django import forms
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase

from game.forms import RatingForm, GameCreateForm, GameSearchForm, PlayerRegistrationForm, PlayerUpdateForm, \
    GenreCreateForm, PublisherCreateForm
from game.models import Rating, Platform, Genre, Publisher, Player


class RatingFormTestCase(TestCase):

    def test_form_initializes_with_correct_model_and_fields(self):
        form = RatingForm()
        self.assertEqual(form.Meta.model, Rating)
        self.assertEqual(list(form.Meta.fields), ["score"])


class GameCreateFormTestCase(TestCase):
    def setUp(self):
        self.genre = Genre.objects.create(name='Test Genre', description='Test Genre')
        self.publisher = Publisher.objects.create(name='Test Publisher', description='Test Publisher', country="Ukraine", capitalization=00.02)
        self.platform = Platform.objects.create(name='Test Platform')


    def test_form_initializes_with_all_fields(self):
        form = GameCreateForm()
        expected_fields = [
            "title", "description", "platform", "release_year",
            "genre", "publisher", "image", "link"
        ]
        self.assertEqual(list(form.fields.keys()), expected_fields)


    def test_display_all_platforms_as_checkboxes(self):
        form = GameCreateForm()
        self.assertIn('platform', form.fields)
        self.assertIsInstance(form.fields['platform'], forms.ModelMultipleChoiceField)
        self.assertEqual(form.fields['platform'].queryset.count(), Platform.objects.all().count())
        self.assertIsInstance(form.fields['platform'].widget, forms.CheckboxSelectMultiple)

    def test_required_fields_presence(self):
        form = GameCreateForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
        self.assertIn('description', form.errors)
        self.assertIn('platform', form.errors)
        self.assertIn('release_year', form.errors)
        self.assertIn('genre', form.errors)
        self.assertIn('publisher', form.errors)
        self.assertIn('image', form.errors)
        self.assertIn('link', form.errors)

    def test_handle_empty_values(self):
        form_data = {
            'title': '',
            'description': None,
            'platform': [],
            'release_year': None,
            'genre': None,
            'publisher': None,
            'image': None,
            'link': ''
        }
        form = GameCreateForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_foreign_key_constraints(self):
        form = GameCreateForm()
        self.assertIn('genre', form.fields)
        self.assertIn('publisher', form.fields)


class GameSearchFormTestCase(TestCase):

    def test_form_initialization(self):
        form = GameSearchForm()
        self.assertEqual(form.fields['title'].required, False)
        self.assertEqual(form.fields['title'].label, "")
        self.assertEqual(form.fields['title'].widget.attrs, {"placeholder": "Search by title", 'maxlength': '255'})

    def test_valid_title_within_max_length(self):
        form_data = {'title': 'A' * 255}
        form = GameSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_placeholder_text(self):
        form = GameSearchForm()
        self.assertEqual(form.fields['title'].widget.attrs['placeholder'], 'Search by title')

    def test_empty_title_submission(self):
        form_data = {"title": ""}
        form = GameSearchForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_title_input_special_characters(self):
        form = GameSearchForm(data={'title': 'Special!@#$%^&*()_+Characters'})
        self.assertTrue(form.is_valid())


class PlayerRegistrationFormTestCase(TestCase):
    def setUp(self):
        self.username = "testuser"
        self.password1 = "password123qwert"
        self.password2 = "password123qwert"

    def test_form_initializes_with_all_fields(self):
        form = PlayerRegistrationForm()
        expected_fields = [
            "username",
            "email",
            "date_of_birth",
            "first_name",
            "last_name",
            "password1",
            "password2",
        ]
        self.assertEqual(list(form.fields.keys()), expected_fields)

    def test_form_validates_with_required_fields(self):
        form_data = {
            "username": self.username,
            "password1": self.password1,
            "password2": self.password2,
        }
        form = PlayerRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_date_of_birth_at_minimum_age_boundary(self):
        min_age_date = (timezone.now() - timedelta(days=365 * 100)).date()
        form_data = {
            "username": self.username,
            "password1": self.password1,
            "password2": self.password2,
            "date_of_birth": min_age_date,
        }
        form = PlayerRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_form_saves_new_player_instance(self):
        form_data = {
            'username': self.username,
            'email': 'test@example.com',
            'date_of_birth': '1990-01-01',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': self.password1,
            'password2': self.password2,
        }
        form = PlayerRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        player = form.save()
        self.assertEqual(player.username, 'testuser')
        self.assertEqual(player.email, 'test@example.com')
        self.assertEqual(player.date_of_birth, date(1990, 1, 1))
        self.assertEqual(player.first_name, 'Test')
        self.assertEqual(player.last_name, 'User')

    def test_date_of_birth_outside_valid_range_triggers_validation_error(self):
        form_data = {
            'username': self.username,
            'email': 'test@example.com',
            'date_of_birth': '1900-01-01',
            'first_name': 'Test',
            'last_name': 'User',
            'password1': self.password1,
            'password2': self.password2,
        }
        form = PlayerRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('date_of_birth', form.errors)

    def test_form_associates_with_player_model(self):
        form = PlayerRegistrationForm()
        self.assertEqual(form.Meta.model, Player)


class PlayerUpdateFormTestCase(TestCase):
    def setUp(self):
        self.player = Player.objects.create(
            first_name="John", last_name="Doe", date_of_birth="1990-01-01"
        )

    def test_form_saves_valid_data(self):
        form_data = {
            "first_name": "Jane",
            "last_name": "Smith",
            "date_of_birth": "1992-02-02"
        }
        form = PlayerUpdateForm(data=form_data, instance=self.player)
        self.assertTrue(form.is_valid())
        updated_player = form.save()
        self.assertEqual(updated_player.first_name, "Jane")
        self.assertEqual(updated_player.last_name, "Smith")
        self.assertEqual(str(updated_player.date_of_birth), "1992-02-02")

    def test_form_initializes_with_existing_data(self):
        form = PlayerUpdateForm(instance=self.player)
        self.assertEqual(form.initial["first_name"], "John")
        self.assertEqual(form.initial["last_name"], "Doe")
        self.assertEqual(str(form.initial["date_of_birth"]), "1990-01-01")

    def test_form_handles_empty_fields(self):
        form_data = {
            "first_name": "",
            "last_name": "",
            "date_of_birth": "1990-01-01"
        }
        form = PlayerUpdateForm(data=form_data, instance=self.player)
        self.assertTrue(form.is_valid())
        updated_player = form.save()
        self.assertEqual(updated_player.first_name, None)
        self.assertEqual(updated_player.last_name, None)

    def test_form_handles_invalid_date_format(self):
        form_data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "invalid-date"
        }
        form = PlayerUpdateForm(data=form_data, instance=self.player)
        self.assertFalse(form.is_valid())
        self.assertIn("date_of_birth", form.errors)

    def test_form_display_correctly(self):
        form = PlayerUpdateForm()
        self.assertIn('first_name', form.fields)
        self.assertIn('last_name', form.fields)
        self.assertIn('date_of_birth', form.fields)

    def test_form_updates_fields_correctly(self):
        form_data = {
            'first_name': 'John',
            'last_name': 'Doe',
            'date_of_birth': '1990-01-01'
        }
        form = PlayerUpdateForm(data=form_data)
        self.assertTrue(form.is_valid())
        player_instance = form.save(commit=False)
        self.assertEqual(player_instance.first_name, 'John')
        self.assertEqual(player_instance.last_name, 'Doe')
        self.assertEqual(player_instance.date_of_birth, date(1990, 1, 1))


class GenreCreateFormTestCase(TestCase):
    def setUp(self):
        self.name = "Action"
        self.description = "Action genre description"
        self.image = None

    def test_form_saves_with_valid_data(self):
        data = {
            'name': self.name,
            'description': self.description,
            'image': None
        }
        form = GenreCreateForm(data=data)
        self.assertTrue(form.is_valid())
        genre = form.save()
        self.assertEqual(genre.name, 'Action')
        self.assertEqual(genre.description, 'Action genre description')

    def test_form_displays_all_fields(self):
        form = GenreCreateForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('image', form.fields)

    def test_form_fails_with_missing_required_fields(self):
        data = {
            'description': self.description,
            'image': None
        }
        form = GenreCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)


class PublisherCreateFormTestCase(TestCase):
    def setUp(self):
        self.name = "Bohdan Ent."
        self.description = "Best company ever"
        self.country = "Liberty Land"
        self.capitalization = Decimal("99.99")
        self.image = None

    def test_form_saves_with_valid_data(self):
        data = {
            'name': self.name,
            'description': self.description,
            'country': self.country,
            'capitalization': self.capitalization,
            'image': None

        }
        form = PublisherCreateForm(data=data)
        self.assertTrue(form.is_valid())
        publisher = form.save()
        self.assertEqual(publisher.name, "Bohdan Ent.")
        self.assertEqual(publisher.description, "Best company ever")
        self.assertEqual(publisher.country, "Liberty Land")
        self.assertEqual(publisher.capitalization, Decimal("99.99"))

    def test_form_displays_all_fields(self):
        form = PublisherCreateForm()
        self.assertIn('name', form.fields)
        self.assertIn('description', form.fields)
        self.assertIn('image', form.fields)
        self.assertIn('country', form.fields)
        self.assertIn('capitalization', form.fields)

    def test_form_fails_with_missing_required_fields(self):
        data = {
            'description': self.description,
            'image': None
        }
        form = PublisherCreateForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)

    def test_handles_maximum_decimal_places(self):
        data = {
            'name': self.name,
            'description': self.description,
            'country': self.country,
            'capitalization': 12345.67
        }
        form = PublisherCreateForm(data=data)
        self.assertFalse(form.is_valid())
