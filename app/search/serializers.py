from rest_framework import serializers

from core.models import Artist

class ArtistSearchSerializer(serializers.ModelSerializer):
    """Serializer for artists."""
    similarity = serializers.FloatField()

    class Meta:
        model = Artist
        fields = ['name', 'origin_country', 'start_year', 'end_year', 'similarity']
        read_only_fields = ['id']