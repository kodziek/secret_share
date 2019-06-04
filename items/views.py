import random
import string

from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.urls import reverse_lazy
from django.views.generic import CreateView

from items.forms import ItemForm


class CreateItemView(CreateView):
    form_class = ItemForm
    template_name = 'items/form.html'
    success_url = reverse_lazy('create-item')

    def _generate_random_password(self):
        characters = string.ascii_letters + string.digits
        return ''.join(random.choice(characters) for _ in range(15))

    def form_valid(self, form):
        password = self._generate_random_password()

        instance = form.save(commit=False)
        instance.user = self.request.user
        instance.password = make_password(password)
        instance.save()

        messages.success(self.request, f'{password} {instance.uuid}')

        return super().form_valid(form)
