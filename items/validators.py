from rest_framework import serializers


class OneOf(object):
    def __init__(self, fields):
        self.fields = fields

    def __call__(self, value):
        if set(self.fields).issubset(value):
            raise serializers.ValidationError(
                f'Expecting just one field from following list: {self.fields}',
            )
