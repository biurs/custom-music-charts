"""
View for List APIs
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
from rest_framework import (
    viewsets,
    mixins,
    status,
)
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import (
    Artist,
    Album,
    List,
    Entry
)
from list import serializers

class ListViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ListDetailSerializer
    queryset = List.objects.all()
    authentication_classes = [TokenAuthentication]


    def get_queryset(self):
        queryset = self.queryset
        public = self.request.query_params.get('public')
        if public:
            return queryset.filter(public=True).order_by('-id')
        return queryset.filter(user=self.request.user).distinct().order_by('-id')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        """Return the serializer class for request."""
        if self.action == 'list':
            return serializers.ListSerializer
        return self.serializer_class