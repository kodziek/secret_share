import json
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.contrib.auth.hashers import check_password, make_password
from django.core.files.uploadedfile import SimpleUploadedFile
from django.urls import reverse_lazy
from freezegun import freeze_time
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_200_OK,
    HTTP_201_CREATED,
    HTTP_302_FOUND,
    HTTP_400_BAD_REQUEST,
    HTTP_401_UNAUTHORIZED,
    HTTP_404_NOT_FOUND,
)
from rest_framework.test import APITestCase

from core.factories import UserFactory
from items.factories import ItemFactory
from items.models import Item


class BaseAPITestCase(APITestCase):
    url = None

    @classmethod
    def setUpTestData(cls):
        cls.user = UserFactory()
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

    def test_retrieve_incorrect_uuid_raises_not_found(self):
        response = self._request(url=f'{self.url}uuid/')
        json_response = json.loads(response.content)

        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(json_response, {'detail': 'Not found.'})

    def test_retrieve_missing_password_raises_not_found(self):
        item = ItemFactory(user=self.user)
        response = self._request(url=f'{self.url}{item.uuid}/')
        json_response = json.loads(response.content)
        item.refresh_from_db()

        self.assertEqual(item.visit_count, 0)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(json_response, {'detail': 'Not found.'})

    def test_retrieve_incorrect_password_raises_not_found(self):
        item = ItemFactory(user=self.user)
        response = self._request(
            url=f'{self.url}{item.uuid}/?password=incorrect',
        )
        json_response = json.loads(response.content)
        item.refresh_from_db()

        self.assertEqual(item.visit_count, 0)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(json_response, {'detail': 'Not found.'})

    def test_retrieve_correct_password_redirects_to_url(self):
        password = 'password'
        item = ItemFactory(
            user=self.user, url='http://kodziek.pl',
            password=make_password(password),
        )

        self.assertEqual(item.visit_count, 0)

        response = self._request(
            url=f'{self.url}{item.uuid}/?password={password}',
        )
        item.refresh_from_db()

        self.assertEqual(item.visit_count, 1)
        self.assertEqual(response.status_code, HTTP_302_FOUND)
        self.assertEqual(response.url, item.url)

    def test_retrieve_correct_password_returns_file(self):
        password = 'password'
        content = b'content'
        item = ItemFactory(
            user=self.user, file=SimpleUploadedFile('file', content),
            password=make_password(password),
        )

        self.assertEqual(item.visit_count, 0)

        response = self._request(
            url=f'{self.url}{item.uuid}/?password={password}',
        )
        item.refresh_from_db()

        self.assertEqual(item.visit_count, 1)
        self.assertEqual(response.status_code, HTTP_200_OK)

        response_content = b''
        for line in response.streaming_content:
            response_content += line

        self.assertEqual(response_content, content)

    def test_retrieve_item_older_than_one_day_returns_not_found(self):
        password = 'password'
        with freeze_time(datetime.now() - relativedelta(days=1, seconds=2)):
            item = ItemFactory(
                user=self.user, url='http://kodziek.pl',
                password=make_password(password),
            )
        response = self._request(
            url=f'{self.url}{item.uuid}/?password={password}',
        )
        item.refresh_from_db()
        json_response = json.loads(response.content)

        self.assertEqual(item.visit_count, 0)
        self.assertEqual(response.status_code, HTTP_404_NOT_FOUND)
        self.assertEqual(json_response, {'detail': 'Not found.'})
