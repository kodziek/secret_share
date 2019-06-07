import factory

from core.models import User


class UserFactory(factory.django.DjangoModelFactory):
    username = factory.Sequence(lambda n: f'user_{n}')

    class Meta:
        model = User
