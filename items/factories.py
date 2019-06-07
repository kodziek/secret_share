import factory

from items.models import Item


class ItemFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Item
