import factory

from items.models import Item


class ItemFactory(factory.Factory):
    class Meta:
        model = Item
