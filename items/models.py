import uuid
from datetime import datetime

from dateutil.relativedelta import relativedelta
from django.conf import settings
from django.db import models, transaction


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
    visit_count = models.PositiveIntegerField(default=0)

    objects = ItemManager.as_manager()
    all_objects = models.Manager()

    def __str__(self):
        return self.url or str(self.file)

    @classmethod
    def increment_visit_count(cls, pk):
        with transaction.atomic():
            item = cls.objects.select_for_update().get(pk=pk)
            item.visit_count += 1
            item.save()
