from django.shortcuts import render
from rest_framework import serializers, fields, views, generics, viewsets
from core.models import Artist, Album
from django.contrib.postgres.search import TrigramSimilarity
from search.serializers import SearchSerializer
from itertools import chain
from operator import attrgetter


from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes,
    OpenApiResponse
)
# Create your views here.

@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'term',
                OpenApiTypes.STR,
                description='Search Term'),
        ],
        responses=OpenApiResponse(
        )

    )
)
class Search(viewsets.ReadOnlyModelViewSet):
    serializer_class = SearchSerializer

    def get_queryset(self):
        term = self.request.query_params.get('term', None)
        if term:
            artist_res = Artist.objects.all().annotate(
                    similarity=TrigramSimilarity('name', term)
                ).filter(
                    similarity__gt=0.3
                )
            album_res = Album.objects.all().annotate(
                    similarity=TrigramSimilarity('title', term)
                ).filter(
                    similarity__gt=0.3
                )
            full_res = list(chain(artist_res, album_res))
            return sorted(full_res, key=attrgetter('similarity'), reverse=True)
        else:
            return Artist.objects.none()

