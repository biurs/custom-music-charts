"""
Views for the recipes APIs.
"""


from rest_framework import (
    viewsets,
    mixins,
    status,
)

from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny, SAFE_METHODS

from django_filters import rest_framework as filters

from core.models import Album, Artist, Genre
from album import serializers


class AlbumViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.AlbumSerializer
    queryset = Album.objects.all().order_by('id')
    authentication_classes = [TokenAuthentication]


    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        else:
            return [IsAdminUser()]

    def _params_to_ints(self, qs):
        """Convert a list of string to integers."""
        return int(qs)

    def perform_create(self, serializer):
        """Create a new album."""
        serializer.save()

    def get_serializer_class(self):
        if self.action == 'upload_image':
            return serializers.AlbumImageSerializer

        return self.serializer_class

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to album."""
        album = self.get_object()
        serializer = self.get_serializer(album, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BaseAlbumAttrViewSet(mixins.DestroyModelMixin,
                           mixins.UpdateModelMixin,
                           mixins.ListModelMixin,
                           viewsets.GenericViewSet):
    """Base viewset for attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        else:
            return [IsAdminUser()]

    def get_queryset(self):
        """Filter queryset."""
        queryset = self.get_queryset
        return queryset.all().order_by('id').distinct()


class ArtistViewSet(BaseAlbumAttrViewSet):
    """Manage artists in the database."""
    serializer_class = serializers.ArtistHelperSerializer
    queryset = Artist.objects.all()

    def perform_create(self, serializer):
        serializer.save()

class GenreViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.GenreSerializer
    queryset = Genre.objects.all().order_by('id')
    authentication_classes = [TokenAuthentication]


    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [AllowAny()]
        else:
            return [IsAdminUser()]

    def perform_create(self, serializer):
        """Create a new album."""
        serializer.save()