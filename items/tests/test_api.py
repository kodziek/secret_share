import json

from django.contrib.auth.hashers import check_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse_lazy
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_201_CREATED,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
)
from rest_framework.test import APITestCase

from core.factories import UserFactory
from items.models import Item


class BaseAPITestCase(APITestCase):
    url = None

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
        cls.user.save()
        cls.token = Token.objects.create(user=cls.user)

    def _request(self, method='get', data=None, url=None):
        return getattr(self.client, method)(
            url or self.url, data,
            HTTP_AUTHORIZATION=f'Token {self.token.key}',
        )


class ItemApiViewSet(BaseAPITestCase):
    url = reverse_lazy('item-list')

    def test_post_unauthorized(self):
        response = self.client.post(self.url, data={})
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_401_UNAUTHORIZED)
        self.assertEqual(
            json_response,
            {'detail': 'Authentication credentials were not provided.'},
        )

    def test_post_authorized_missing_data(self):
        response = self._request('post', {})
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json_response,
            {
                'non_field_errors': [
                    'One of following fields is required: '
                    '(\'url\', \'file\').',
                ],
            },
        )

    def test_post_authorized_both_fields_url_and_file(self):
        data = {
            'url': 'http://kodziek.pl',
            'file': SimpleUploadedFile('file', b'content'),
        }
        response = self._request('post', data)
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json_response,
            {
                'non_field_errors': [
                    'Expecting just one field from following list: '
                    '(\'url\', \'file\').',
                ],
            },
        )

    def test_post_authorized_incorrect_url(self):
        data = {'url': 'incorrect'}
        response = self._request('post', data)
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(json_response, {'url': ['Enter a valid URL.']})

    def test_post_authorized_incorrect_file(self):
        data = {'file': 'incorrect'}
        response = self._request('post', data)
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_400_BAD_REQUEST)
        self.assertEqual(
            json_response,
            {
                'file': [
                    'The submitted data was not a file. '
                    'Check the encoding type on the form.',
                ],
            },
        )

    def test_post_authorized_correct_url(self):
        data = {
            'url': 'http://kodziek.pl',
        }
        response = self._request('post', data)
        json_response = json.loads(response.content)
        item = Item.objects.get(user=self.user, url=data['url'])

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(tuple(json_response.keys()), ('url', 'password'))
        self.assertTrue(
            check_password(json_response['password'], item.password),
        )
        self.assertEqual(str(item.uuid), json_response['url'][-37:-1])
        self.assertEqual(item.file.name, '')

    def test_post_authorized_correct_file(self):
        data = {
            'file': SimpleUploadedFile('file', b'content'),
        }
        response = self._request('post', data)
        json_response = json.loads(response.content)
        item = Item.objects.get(user=self.user)

        self.assertEqual(response.status_code, HTTP_201_CREATED)
        self.assertEqual(tuple(json_response.keys()), ('url', 'password'))
        self.assertTrue(
            check_password(json_response['password'], item.password),
        )
        self.assertEqual(str(item.uuid), json_response['url'][-37:-1])
        self.assertIsNotNone(item.file)
