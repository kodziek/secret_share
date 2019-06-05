from django.urls import reverse
from rest_framework import serializers

from core.helpers import generate_random_password
from items.models import Item


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('uuid',)


class ItemResponseSerializer(serializers.Serializer):
    url = serializers.SerializerMethodField()
    password = serializers.CharField()

    def get_url(self, obj):
        return reverse('item-detail', kwargs={'uuid': obj.uuid})


class ItemCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(required=False)

    class Meta:
        model = Item
        fields = ('url', 'file', 'password')

    def create(self, validated_data):
        password = generate_random_password()
        item = Item.objects.create(
            user=self.context['request'].user, password=password,
            **validated_data,
        )
        return item

    def to_representation(self, instance):
        return ItemResponseSerializer(instance).data
