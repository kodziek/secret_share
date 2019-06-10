import uuid
from datetime import datetime

from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models, transaction

private_storage = FileSystemStorage(
    location=f'{settings.BASE_DIR}{settings.PRIVATE_MEDIA}',
)


class ItemManager(models.Manager):
    def get_queryset(self):
        timedelta = datetime.now() - settings.ITEMS_LIFETIME
        return super().get_queryset().filter(create_date__gt=timedelta)


class Item(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
    )
    create_date = models.DateTimeField(auto_now_add=True, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    password = models.CharField(max_length=128)
    url = models.TextField(null=True, blank=True)
    file = models.FileField(null=True, blank=True, storage=private_storage)
    visit_count = models.PositiveIntegerField(default=0)

    objects = ItemManager()
    all_objects = models.Manager()

    def __str__(self):
        return self.url or str(self.file)

    @classmethod
    def increment_visit_count(cls, pk):
        with transaction.atomic():
            item = cls.objects.select_for_update().get(pk=pk)
            item.visit_count += 1
            item.save()
