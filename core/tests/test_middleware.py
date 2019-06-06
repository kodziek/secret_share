from unittest.mock import MagicMock, PropertyMock

from django.contrib.auth.models import AnonymousUser
from django.test import TestCase

from core.factories import UserFactory
from core.middleware import UserAgentMiddleware


class UserAgentMiddlewareTestCase(TestCase):
    def setUp(self):
        self.middleware = UserAgentMiddleware(lambda request: None)

    def _get_request(self, user):
        request = MagicMock()
        type(request).headers = PropertyMock(
            return_value={'User-Agent': 'Test UA'},
        )
        request.user = user
        return request

    def test_anonymous_user_has_no_last_user_agent(self):
        user = AnonymousUser()
        request = self._get_request(user)
        self.middleware(request)
        self.assertIsNone(getattr(user, 'last_user_agent', None))

    def test_authenticated_user_has_updated_last_user_agent(self):
        user = UserFactory()
        self.assertEqual(user.last_user_agent, '')
        request = self._get_request(user)
        self.middleware(request)
        self.assertEqual(user.last_user_agent, request.headers['User-Agent'])
