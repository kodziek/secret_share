from django.urls import path

from items.views import CreateItemView

app_name = 'items'

urlpatterns = [
    path('create/', CreateItemView.as_view(), name='create'),
]
