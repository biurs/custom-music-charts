"""
Serializers for the Album APIS.
"""
from rest_framework import serializers

from django.contrib.auth.validators import UnicodeUsernameValidator

from core.models import Album, Artist


class ArtistHelperSerializer(serializers.ModelSerializer):
    """Serializer for artists."""

    class Meta:
        model = Artist
        fields = ['id', 'name']
        extra_kwargs = {
            'name': {
                'validators': []
            }
        }


class AlbumSerializer(serializers.ModelSerializer):
    """Serializer for albums."""
    artist = ArtistHelperSerializer(many=False, required=True)
    release_date = serializers.DateField()

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'release_date', 'avg_rating', 'rating_count', 'link']
        read_only_fields = ['id']


    def _get_or_create_artist(self, artist_name):
        """Handle getting or creating artists as needed."""
        try:
            artist_obj = Artist.objects.get(name=artist_name)
        except Artist.DoesNotExist:
            artist_obj = Artist.objects.create(name=artist_name)
        return artist_obj

    def create(self, validated_data):
        """Create an album."""
        artist_data = validated_data.pop('artist')
        artist_name = artist_data.pop('name')
        artist = self._get_or_create_artist(artist_name)
        album = Album.objects.create(artist=artist, **validated_data)

        return album

    def update(self, instance, validated_data):
        """Update an album."""
        artist_data = validated_data.pop('artist', None)
        if artist_data:
            artist_name = artist_data.pop('name')
            artist = self._get_or_create_artist(artist_name)
            instance.artist = artist

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance