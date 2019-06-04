from django.urls import path

from items.views import CreateItemView, GetItemView

app_name = 'items'

urlpatterns = [
    path('create/', CreateItemView.as_view(), name='create'),
    path('<uuid:uuid>', GetItemView.as_view(), name='get'),
]
