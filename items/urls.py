from django.urls import path

from items.views import CreateItemView

urlpatterns = [
    path('create/', CreateItemView.as_view(), name='create-item'),
]
