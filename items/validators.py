from rest_framework.exceptions import ValidationError


class OneOf(object):
    def __init__(self, fields):
        self.fields = fields

    def __call__(self, value):
        if set(self.fields).issubset(value):
            raise ValidationError(
                'Expecting just one field from following list: '
                f'{self.fields}.',
            )
        if not value:
            raise ValidationError(
                f'One of following fields is required: {self.fields}.',
            )
