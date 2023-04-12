"""
Views for the recipes APIs.
"""


from rest_framework import (
    viewsets,
    mixins,
    status,
)


from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Album, Artist
from album import serializers


class AlbumViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.AlbumSerializer
    queryset = Album.objects.all().order_by('-id')
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of string to integers."""
        return int(qs)

    def perform_create(self, serializer):
        """Create a new album."""
        serializer.save()


class BaseAlbumAttrViewSet(mixins.DestroyModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """Base viewset for attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Filter queryset."""
        queryset = self.get_queryset
        return queryset.all().order_by('-name').distinct()


class ArtistViewSet(BaseAlbumAttrViewSet):
    """Manage artists in the database."""
    serializer_class = serializers.ArtistSerializer
    queryset = Artist.objects.all()

    def perform_create(self, serializer):
        serializer.save()