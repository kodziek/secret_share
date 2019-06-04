import uuid
from django.conf import settings
from django.db import models


class Item(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
    )
    create_date = models.DateTimeField(auto_now_add=True, editable=False)
    uuid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    password = models.CharField(max_length=128)
    url = models.TextField(null=True, blank=True)
    file = models.FileField(null=True, blank=True)

    def __str__(self):
        return self.url or str(self.file)
