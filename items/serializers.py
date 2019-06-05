from django.contrib.auth.hashers import make_password
from django.urls import reverse
from rest_framework import serializers

from core.helpers import generate_random_password
from items.models import Item
from items.validators import OneOf


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('uuid',)


class ItemResponseSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField()
    password = serializers.CharField()

    def get_url(self, obj):
        return self.context.build_absolute_uri(
            reverse('item-detail', kwargs={'uuid': obj.uuid})
        )


class ItemCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)
    url = serializers.URLField(required=False)

    class Meta:
        model = Item
        fields = ('url', 'file', 'password')
        validators = [
            OneOf(('url', 'file')),
        ]

    def create(self, validated_data):
        password = generate_random_password()
        item = Item.objects.create(
            user=self.context['request'].user,
            password=make_password(password),
            **validated_data,
        )
        # hack to show plain text password in API response
        item.password = password
        return item

    def to_representation(self, instance):
        return ItemResponseSerializer(
            instance, context=self.context['request'],
        ).data
