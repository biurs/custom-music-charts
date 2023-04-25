"""
Views for the recipes APIs.
"""
from rest_framework import (
    viewsets,
    mixins,
    status,
)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser, SAFE_METHODS

from django_filters import rest_framework as filters

from django.db.models import Q

from core.models import Album, Artist
from artist import serializers


class ArtistViewSet(viewsets.ModelViewSet):
    """View for manage recipe APIs."""
    serializer_class = serializers.ArtistSerializer
    queryset = Artist.objects.all()
    authentication_classes = [TokenAuthentication]
    filter_backends = [filters.DjangoFilterBackend]
    filterset_fields = ['origin_country']


    def get_permissions(self):
        if self.request.method in SAFE_METHODS:
            return [IsAuthenticated()]
        else:
            return [IsAdminUser()]

    def perform_create(self, serializer):
        """Create a new album."""
        serializer.save()

    def get_queryset(self):
        """Retrieve artists queryset."""
        year = self.request.query_params.get('year')
        queryset = self.queryset
        if year:
            yearlist = year.split(',')
            if len(yearlist) == 1:
                yearlist.insert(1, yearlist[0])
            yearrange = range(int(yearlist[0]), int(yearlist[1]) + 1)
            for year in yearrange:
                queryset = queryset.filter(
                Q(start_year__lte=year, end_year=None) |
                Q(start_year__lte=year, end_year__gte=year)
                )
        return queryset.order_by('-id').distinct()


