from django.contrib import admin

from items.models import Item

admin.site.register(Item, admin.ModelAdmin)
