"""
Serializers for the artist APIs.
"""
from rest_framework import serializers

from core.models import Album, Artist

class ArtistSerializer(serializers.ModelSerializer):
    """Serializer for artists."""

    class Meta:
        model = Artist
        fields = ['id', 'name', 'origin_country', 'start_year', 'end_year']
        read_only_fields = ['id']