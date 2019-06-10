from datetime import datetime

from django.conf import settings
from django.contrib.auth.hashers import make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse, reverse_lazy
from freezegun import freeze_time

from core.factories import UserFactory
from items.factories import ItemFactory
from items.models import Item


class CreateItemViewTestCase(TestCase):
    url = reverse_lazy('items:create')

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_unauthorized_redirects_to_login_page(self):
        response = self.client.get(self.url)
        login_url = reverse('login')

        self.assertRedirects(response, f'{login_url}?next={self.url}')

    def test_get_method_renders_item_form(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_post_empty_form_raises_error(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', '__all__',
            ['One of following fields is required: url or file.'],
        )
        self.assertEqual(Item.objects.count(), 0)

    def test_post_incorrect_url_raises_error(self):
        self.client.force_login(self.user)
        data = {
            'url': 'incorrect',
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', 'url', ['Enter a valid URL.'],
        )
        self.assertEqual(Item.objects.count(), 0)

    def test_post_send_both_fields_raises_error(self):
        self.client.force_login(self.user)
        data = {
            'url': 'http://kodziek.pl',
            'file': SimpleUploadedFile('file', b'content'),
        }
        response = self.client.post(self.url, data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', '__all__',
            ['Cannot use both fields (url and file) at the same time.'],
        )
        self.assertEqual(Item.objects.count(), 0)

    def test_post_create_item_with_url(self):
        self.client.force_login(self.user)
        data = {
            'url': 'http://kodziek.pl',
        }
        response = self.client.post(self.url, data)
        items = Item.objects.filter(url=data['url'], user=self.user)

        self.assertRedirects(response, self.url)
        self.assertEqual(items.count(), 1)

    def test_post_create_item_with_file(self):
        self.client.force_login(self.user)
        data = {
            'file': SimpleUploadedFile('file', b'content'),
        }
        response = self.client.post(self.url, data)
        items = Item.objects.filter(url='', file__isnull=False, user=self.user)

        self.assertRedirects(response, self.url)
        self.assertEqual(items.count(), 1)


class GetItemViewTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.file_content = b'content'
        cls.password = 'password'
        cls.password_encrypted = make_password(cls.password)
        with freeze_time(datetime.now() - settings.ITEMS_LIFETIME):
            cls.old_item = ItemFactory(
                user=cls.user, url=reverse('login'),
                password=cls.password_encrypted,
            )
            cls.old_item_url = reverse(
                'items:get', kwargs={'uuid': cls.old_item.uuid},
            )

    def setUp(self):
        self.url_item = ItemFactory(
            user=self.user, url=reverse('login'),
            password=self.password_encrypted,
        )
        self.file_item = ItemFactory(
            user=self.user, file=SimpleUploadedFile('file', self.file_content),
            password=self.password_encrypted,
        )
        self.url_item_url = reverse(
            'items:get', kwargs={'uuid': self.url_item.uuid},
        )
        self.file_item_url = reverse(
            'items:get', kwargs={'uuid': self.file_item.uuid},
        )

    def test_get_renders_password_form(self):
        response = self.client.get(self.url_item_url)

        self.assertEqual(response.status_code, 200)

    def test_get_old_file_raises_404_not_found(self):
        response = self.client.get(self.old_item_url)

        self.assertEqual(response.status_code, 404)

    def test_post_missing_data_raises_error(self):
        response = self.client.post(self.url_item_url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', 'password', ['This field is required.'],
        )

    def test_post_incorrect_password_raises_error(self):
        data = {
            'password': 'incorrect',
        }
        response = self.client.post(self.url_item_url, data)

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', 'password', ['Incorrect password.'],
        )

    def test_post_redirect_to_item_url(self):
        data = {
            'password': self.password,
        }
        response = self.client.post(self.url_item_url, data)
        self.url_item.refresh_from_db()

        self.assertRedirects(response, self.url_item.url)
        self.assertEqual(self.url_item.visit_count, 1)

    def test_post_returns_file(self):
        data = {
            'password': self.password,
        }
        response = self.client.post(self.file_item_url, data)
        self.file_item.refresh_from_db()

        response_content = b''
        for line in response.streaming_content:
            response_content += line

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_content, self.file_content)
        self.assertEqual(self.file_item.visit_count, 1)

    def test_post_to_old_file_raises_404_not_found(self):
        data = {
            'password': self.password,
        }
        response = self.client.post(self.old_item_url, data)
        self.old_item.refresh_from_db()

        self.assertEqual(response.status_code, 404)
        self.assertEqual(self.url_item.visit_count, 0)
