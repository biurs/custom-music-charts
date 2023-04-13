"""
Serializers for the album APIs.
"""
from rest_framework import serializers

from core.models import Album, Artist

class ArtistSerializer(serializers.ModelSerializer):
    """Serializer for artists."""

    class Meta:
        model = Artist
        fields = ['id', 'name', 'origin_country', 'years_active']
        read_only_fields = ['id']