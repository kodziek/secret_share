from django.contrib import admin

from items.forms import ItemPasswordForm
from items.models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    fields = ('password',)
    list_display = ('uuid', '__str__', 'create_date')
    form = ItemPasswordForm
