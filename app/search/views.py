from django.shortcuts import render
from rest_framework import serializers, fields, views, generics, viewsets
from core.models import Artist
from django.contrib.postgres.search import TrigramSimilarity
from search.serializers import ArtistSearchSerializer

from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
)
# Create your views here.

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'term',
                OpenApiTypes.STR,
                description='Search Term'),
        ]
    )
)
class SearchArtist(viewsets.ReadOnlyModelViewSet):
    model = Artist
    queryset = Artist.objects.all()
    serializer_class = ArtistSearchSerializer

    def get_queryset(self):
        term = self.request.query_params.get('term', None)
        if term:
            return self.queryset.annotate(
                similarity=TrigramSimilarity('name', term)
            ).filter(
                similarity__gt=0.3
            ).order_by('-similarity')

        else:
            return None