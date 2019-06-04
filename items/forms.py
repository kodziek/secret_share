from django import forms
from django.contrib.auth.hashers import check_password, make_password
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


class ItemAccessForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput)

    def __init__(self, object, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.object = object

    def clean(self):
        password = self.cleaned_data.get('password')
        if not check_password(password, self.object.password):
            raise ValidationError('Incorrect password.')
        return self.cleaned_data


class ItemPasswordForm(forms.ModelForm):
    class Meta:
        fields = ('password',)
        widgets = {
            'password': forms.PasswordInput,
        }

    def clean_password(self):
        password = self.cleaned_data.get('password')
        return make_password(password)
