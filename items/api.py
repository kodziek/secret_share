from django.contrib.auth.hashers import check_password
from django.http import Http404, FileResponse
from django.shortcuts import redirect
from rest_framework.generics import RetrieveAPIView

from items.models import Item
from items.serializers import ItemSerializer


class GetItemApiView(RetrieveAPIView):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    lookup_field = 'uuid'
    http_method_names = ('get',)

    def get_object(self):
        obj = super().get_object()
        password = self.request.query_params.get('password')
        if not check_password(password, obj.password):
            raise Http404
        return obj

    def get(self, request, *args, **kwargs):
        item = self.get_object()
        Item.increment_visit_count(item.pk)
        if item.url:
            return redirect(item.url)
        return FileResponse(item.file)
