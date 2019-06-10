from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse, reverse_lazy

from core.factories import UserFactory
from items.models import Item


class CreateItemViewTestCase(TestCase):
    url = reverse_lazy('items:create')

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()

    def test_unauthorized(self):
        response = self.client.get(self.url)
        login_url = reverse('login')

        self.assertRedirects(response, f'{login_url}?next={self.url}')

    def test_get_method(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)

    def test_post_empty_form(self):
        self.client.force_login(self.user)
        response = self.client.post(self.url, {})

        self.assertEqual(response.status_code, 200)
        self.assertFormError(
            response, 'form', '__all__',
            ['One of following fields is required: url or file.'],
        )
        self.assertEqual(Item.objects.count(), 0)

    def test_post_incorrect_url(self):
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

    def test_post_both_fields_error(self):
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
