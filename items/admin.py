from django.contrib import admin

from items.forms import ItemPasswordForm
from items.models import Item


@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    fields = ('password',)
    list_display = ('uuid', '__str__', 'create_date')
    form = ItemPasswordForm

    def get_queryset(self, request):
        return self.model.all_objects.all()

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
