import random
import string

from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic import CreateView, FormView

from items.forms import ItemAccessForm, ItemForm
from items.models import Item


class CreateItemView(LoginRequiredMixin, CreateView):
    form_class = ItemForm
    template_name = 'items/create.html'
    success_url = reverse_lazy('items:create')

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


class GetItemView(FormView):
    form_class = ItemAccessForm
    template_name = 'items/get.html'
    object = None

    def dispatch(self, request, *args, **kwargs):
        self.object = get_object_or_404(Item, uuid=kwargs['uuid'])
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return self.object.url

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['object'] = self.object
        return kwargs

    def form_valid(self, form):
        Item.increment_visit_count(self.object.pk)
        if self.object.file:
            return FileResponse(self.object.file)

        return super().form_valid(form)
