import uuid
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models


class ItemManager(models.QuerySet):

    def filter(self, *args, **kwargs):
        yesterday = datetime.now() - relativedelta(days=1)
        return super().filter(create_date__gte=yesterday, *args, **kwargs)


class Item(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
    )
    create_date = models.DateTimeField(auto_now_add=True, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    password = models.CharField(max_length=128)
    url = models.TextField(null=True, blank=True)
    file = models.FileField(null=True, blank=True)

    objects = ItemManager.as_manager()

    def __str__(self):
        return self.url or str(self.file)
