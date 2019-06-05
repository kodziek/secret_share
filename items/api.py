from django.contrib.auth.hashers import check_password
from django.http import Http404, FileResponse
from django.shortcuts import redirect
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ModelViewSet

from items.models import Item
from items.serializers import ItemSerializer, ItemCreateSerializer


class ItemApiViewSet(ModelViewSet):
    queryset = Item.objects.all()
    lookup_field = 'uuid'
    http_method_names = ('get', 'post')
    parser_classes = (MultiPartParser,)

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated()]
        return []

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return ItemSerializer
        return ItemCreateSerializer

    def get_object(self):
        obj = super().get_object()
        password = self.request.query_params.get('password')
        if not check_password(password, obj.password):
            raise Http404
        return obj

    def retrieve(self, request, *args, **kwargs):
        item = self.get_object()
        Item.increment_visit_count(item.pk)
        if item.url:
            return redirect(item.url)
        return FileResponse(item.file)
