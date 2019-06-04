from django import forms
from django.core.exceptions import ValidationError

from items.models import Item


class ItemForm(forms.ModelForm):
    class Meta:
        fields = ('url', 'file')
        model = Item
        widgets = {
            'url': forms.TextInput,
        }
        field_classes = {
            'url': forms.URLField,
        }

    def clean(self):
        url = self.cleaned_data.get('url')
        file = self.cleaned_data.get('file')

        if not any([url, file]):
            raise ValidationError(
                'One of following fields is required: url or file.',
            )

        if all([url, file]):
            raise ValidationError(
                'Cannot use both fields (url and file) at the same time.',
            )

        return self.cleaned_data
