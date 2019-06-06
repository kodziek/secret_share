from django.test import TestCase
from freezegun import freeze_time

from core.factories import UserFactory
from items.factories import ItemFactory
from items.models import Item


class ItemModelTestCase(TestCase):
    yesterday = '2000-01-01 00:00:00'
    almost_yesterday = '2000-01-01 00:00:01'
    today = '2000-01-02 00:00:00'
    @classmethod
    def setUpTestData(cls):
        user = UserFactory()
        user.save()
        with freeze_time(cls.yesterday):
            cls._create_item(user)
        with freeze_time(cls.almost_yesterday):
            cls._create_item(user)
        with freeze_time(cls.today):
            cls._create_item(user)

    @classmethod
    def _create_item(cls, user):
        ItemFactory(password='a', user=user).save()

    @freeze_time(today)
    def test_default_manager_returns_only_today_item(self):
        self.assertEqual(Item.objects.all().count(), 2)

    @freeze_time(today)
    def test_all_objects_manager_returns_only_today_item(self):
        self.assertEqual(Item.all_objects.all().count(), 3)
