from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from freezegun import freeze_time

from core.factories import UserFactory
from items.factories import ItemFactory
from items.models import Item


class ItemModelTestCase(TestCase):
    today = datetime.now()
    too_old = today - settings.ITEMS_LIFETIME
    almost_too_old = too_old + relativedelta(seconds=5)

    @classmethod
    def setUpTestData(cls):
        user = UserFactory()
        with freeze_time(cls.too_old):
            cls.url_item = cls._create_item(user, url='http://kodziek.pl')
        with freeze_time(cls.almost_too_old):
            cls.file_item = cls.file_url = cls._create_item(
                user, file=SimpleUploadedFile('file', b'content'),
            )
        with freeze_time(cls.today):
            cls._create_item(user)

    @classmethod
    def _create_item(cls, user, **kwargs):
        return ItemFactory(password='a', user=user, **kwargs)

    @freeze_time(today)
    def test_default_manager_returns_only_active_items(self):
        self.assertEqual(Item.objects.all().count(), 2)

    @freeze_time(today)
    def test_all_objects_manager_returns_all_items(self):
        self.assertEqual(Item.all_objects.all().count(), 3)

    def test_str_for_item_with_url(self):
        self.assertEqual(str(self.url_item), self.url_item.url)

    def test_str_for_item_with_fiel(self):
        self.assertEqual(str(self.file_item), self.file_item.file)
