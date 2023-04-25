"""
Views for the lsits APIs.
"""
from rest_framework import (
    viewsets,
    mixins,
    status,
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from django_filters import rest_framework as filters

from django.db.models import Q

from core.models import Album, Artist, List
from list import serializers


class ListViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.ListSerializer
    queryset = List.objects.all()
    authentication_classes = [TokenAuthentication]


    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE', 'POST']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Create a new album."""
        serializer.save()

    def get_queryset(self):
        """Retrieve artists queryset."""
        queryset = self.queryset
        #if user is not staff, only return public lists
        if self.request.user.is_staff == False:
            queryset = queryset.filter(is_public=True)
        return queryset.order_by('id').distinct()



