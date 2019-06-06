from datetime import datetime

import factory

from items.models import Item


class ItemFactory(factory.Factory):
    create_date = factory.LazyFunction(datetime.now)

    class Meta:
        model = Item
