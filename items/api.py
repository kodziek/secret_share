from django.contrib.auth.hashers import check_password
from django.http import FileResponse, Http404
from django.shortcuts import redirect
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from items.models import Item
from items.serializers import ItemCreateSerializer, ItemSerializer


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


class StatsApiViewSet(ModelViewSet):
    http_method_names = ('get',)
    renderer_classes = (JSONRenderer,)
    queryset = Item.all_objects.all()
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(visit_count__gt=0)

    def _format_response(self, queryset):
        response = {}
        for item in queryset:
            create_date = item.create_date.strftime('%Y-%m-%d')
            if create_date not in response:
                response[create_date] = {
                    'files': 0,
                    'links': 0,
                }
            response[create_date]['links' if item.url else 'files'] += 1
        return response

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        response = self._format_response(queryset)
        return Response(response)
