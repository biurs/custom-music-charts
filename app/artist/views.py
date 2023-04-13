"""
Views for the recipes APIs.
"""
from rest_framework import (
    viewsets,
    mixins,
    status,
)


from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from core.models import Album, Artist
from artist import serializers


class ArtistViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.ArtistSerializer
    queryset = Artist.objects.all().order_by('-id')
    authentication_classes = [TokenAuthentication]


    def get_permissions(self):
        if self.request.method in ['PUT', 'PATCH', 'DELETE', 'POST']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def perform_create(self, serializer):
        """Create a new album."""
        serializer.save()