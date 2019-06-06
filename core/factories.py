import factory

from core.models import User


class UserFactory(factory.Factory):
    username = factory.Sequence(lambda n: f'user_{n}')

    class Meta:
        model = User
