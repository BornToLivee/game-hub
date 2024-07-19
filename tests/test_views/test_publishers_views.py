from decimal import Decimal
from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from game.models import Publisher, Game, Genre


class PublisherListViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.publishers = [
            Publisher.objects.create(name=f"Publisher {i}", country="USA", description=f"Description {i}", capitalization=Decimal("00.02")) for i in range(3)
        ]
        self.publishers.append(Publisher.objects.create(name="Publisher Other", country="UK"))

    def test_uses_correct_template(self):
        response = self.client.get(reverse('game:publisher-list'))
        self.assertTemplateUsed(response, 'game/publisher_list.html')

    def test_filter_by_country(self):
        response = self.client.get(reverse('game:publisher-list') + '?country=USA')
        self.assertEqual(response.status_code, 200)
        publishers = response.context['publisher_list']
        self.assertEqual(len(publishers), 3)
        self.assertTrue(all(publisher.country == "USA" for publisher in publishers))

    def test_sorting(self):
        response = self.client.get(reverse('game:publisher-list') + '?ordering=name')
        self.assertEqual(response.status_code, 200)
        publishers = response.context['publisher_list']
        names = [publisher.name for publisher in publishers]
        self.assertEqual(names, sorted(names))

    def test_filter_and_sort(self):
        response = self.client.get(reverse('game:publisher-list') + '?country=USA&ordering=name')
        self.assertEqual(response.status_code, 200)
        publishers = response.context['publisher_list']
        self.assertTrue(all(publisher.country == "USA" for publisher in publishers))
        names = [publisher.name for publisher in publishers]
        self.assertEqual(names, sorted(names))

    def test_context_data(self):
        response = self.client.get(reverse('game:publisher-list'))
        self.assertEqual(response.status_code, 200)
        context = response.context
        self.assertIn('countries', context)
        self.assertIn('selected_country', context)
        self.assertIn('selected_ordering', context)
        expected_countries = ["UK", "USA"]
        for country in expected_countries:
            self.assertIn(country, context['countries'])
        self.assertEqual(context['selected_country'], "")
        self.assertEqual(context['selected_ordering'], "")

    def test_no_query_params(self):
        response = self.client.get(reverse('game:publisher-list'))
        self.assertEqual(response.status_code, 200)
        publishers = response.context['publisher_list']
        self.assertEqual(len(publishers), 4)


class PublisherDetailViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.publisher = Publisher.objects.create(
            name="Test Publisher",
            description="Test Description",
            country="Test Country",
            capitalization=Decimal("00.02"),
        )
        self.genre = Genre.objects.create(name="Test Genre", description="Test Genre Desc.")
        self.game1 = Game.objects.create(
            title="Game 1",
            description="Description 1",
            release_year=2020,
            publisher=self.publisher,
            genre=self.genre,
            link="http://example1.com"
        )
        self.game2 = Game.objects.create(
            title="Game 2",
            description="Description 2",
            release_year=2021,
            publisher=self.publisher,
            genre=self.genre,
            link="http://example2.com"
        )

    def test_publisher_detail_view_uses_correct_template(self):
        response = self.client.get(reverse('game:publisher-detail', kwargs={'pk': self.publisher.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "game/publisher_detail.html")

    def test_publisher_detail_view_context_data(self):
        response = self.client.get(reverse('game:publisher-detail', kwargs={'pk': self.publisher.pk}))
        self.assertEqual(response.status_code, 200)
        context = response.context_data
        self.assertEqual(context["publisher"], self.publisher)
        self.assertIn(self.game1, context["games"])
        self.assertIn(self.game2, context["games"])

    def test_publisher_detail_view_no_games(self):
        publisher_no_games = Publisher.objects.create(name="No Games Publisher", country="No Country")
        response = self.client.get(reverse('game:publisher-detail', kwargs={'pk': publisher_no_games.pk}))
        self.assertEqual(response.status_code, 200)
        context = response.context_data
        self.assertEqual(context["publisher"], publisher_no_games)
        self.assertEqual(len(context["games"]), 0)

    def test_publisher_detail_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('game:publisher-detail', kwargs={'pk': self.publisher.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/publishers/{self.publisher.id}/')


class PublisherCreateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

    def test_publisher_create_view_uses_correct_template(self):
        response = self.client.get(reverse('game:publisher-create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/publisher_create_form.html')

    def test_publisher_create_view_successful(self):
        form_data = {
            'name': 'New Publisher',
            'country': 'New Country',
            "description": "New Description",
            "capitalization": Decimal("00.02"),
        }
        response = self.client.post(reverse('game:publisher-create'), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('game:publisher-list'))
        self.assertTrue(Publisher.objects.filter(name='New Publisher').exists())

    def test_publisher_create_view_invalid_data(self):
        form_data = {
            'name': '',
            'country': 'New Country',
            "description": "New Description",
            "capitalization": Decimal("00.02"),
        }
        response = self.client.post(reverse('game:publisher-create'), data=form_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('name', form.errors)
        self.assertEqual(form.errors['name'], ['This field is required.'])

    def test_publisher_create_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('game:publisher-create'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={reverse("game:publisher-create")}')


class PublisherUpdateViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        self.publisher = Publisher.objects.create(
            name='Existing Publisher',
            country='Existing Country',
            description='Existing Description',
            capitalization=Decimal('10.00')
        )

    def test_publisher_update_view_uses_correct_template(self):
        response = self.client.get(reverse('game:publisher-update', kwargs={'pk': self.publisher.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/publisher_create_form.html')

    def test_publisher_update_view_successful(self):
        form_data = {
            'name': 'Updated Publisher',
            'country': 'Updated Country',
            'description': 'Updated Description',
            'capitalization': Decimal('20.00')
        }
        response = self.client.post(reverse('game:publisher-update', kwargs={'pk': self.publisher.pk}), data=form_data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('game:publisher-detail', kwargs={'pk': self.publisher.pk}))
        self.publisher.refresh_from_db()
        self.assertEqual(self.publisher.name, 'Updated Publisher')
        self.assertEqual(self.publisher.country, 'Updated Country')
        self.assertEqual(self.publisher.description, 'Updated Description')
        self.assertEqual(self.publisher.capitalization, Decimal('20.00'))

    def test_publisher_update_view_invalid_data(self):
        form_data = {
            'name': '',
            'country': 'Updated Country',
            'description': 'Updated Description',
            'capitalization': Decimal('20.00')
        }
        response = self.client.post(reverse('game:publisher-update', kwargs={'pk': self.publisher.pk}), data=form_data)
        self.assertEqual(response.status_code, 200)
        form = response.context['form']
        self.assertTrue(form.errors)
        self.assertIn('name', form.errors)
        self.assertEqual(form.errors['name'], ['This field is required.'])

    def test_update_view_requires_login(self):
        self.client.logout()
        response = self.client.get(reverse('game:publisher-update', kwargs={'pk': self.publisher.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next={reverse("game:publisher-update", kwargs={"pk": self.publisher.pk})}')


class PublisherDeleteViewTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')
        self.publisher = Publisher.objects.create(
            name='Publisher to Delete',
            country='Some Country',
            description='Some Description',
            capitalization=Decimal('15.00')
        )

    def test_publisher_delete_view_successful(self):
        response = self.client.post(reverse('game:publisher-delete', kwargs={'pk': self.publisher.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('game:publisher-list'))
        self.assertFalse(Publisher.objects.filter(pk=self.publisher.pk).exists())

    def test_publisher_delete_view_get(self):
        response = self.client.get(reverse('game:publisher-delete', kwargs={'pk': self.publisher.pk}))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'game/publisher_confirm_delete.html')

    def test_delete_view_requires_login(self):
        self.client.logout()
        response = self.client.post(reverse('game:publisher-delete', kwargs={'pk': self.publisher.pk}))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f'/accounts/login/?next=/publishers/{self.publisher.pk}/delete/')
