"""
Serializers for the Album APIS.
"""
from rest_framework import serializers

from django.contrib.auth.validators import UnicodeUsernameValidator

from core.models import Album, Artist, Genre


class ArtistHelperSerializer(serializers.ModelSerializer):
    """Serializer for artists."""
    class Meta:
        model = Artist
        fields = ['id', 'name']
        read_only_fields = ['id']
        extra_kwargs = {
            'name': {
                'validators': []
            }
        }


class GenreSerializer(serializers.ModelSerializer):
    """Serializer for genres."""

    class Meta:
        model = Genre
        fields = ['id', 'name']
        read_only_fields = ['id']
        extra_kwargs = {
                'name': {
                    'validators': []
                }
        }

class GenreDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ['id', 'name', 'description']
        read_only_fields = ['id']



class AlbumSerializer(serializers.ModelSerializer):
    """Serializer for albums."""
    artist = ArtistHelperSerializer(many=True, required=False)
    release_date = serializers.DateField()
    primary_genres = GenreSerializer(many=True, required=False)
    secondary_genres = GenreSerializer(many=True, required=False)

    class Meta:
        model = Album
        fields = ['id', 'title', 'artist', 'release_date', 'avg_rating', 'rating_count', 'link', 'primary_genres', 'secondary_genres',]
        read_only_fields = ['id']


    def _get_or_create_artist(self, artists, album):
        """Handle getting or creating artists as needed."""
        for artist in artists:
            artist_obj = Artist.objects.get_or_create(**artist)[0]
            album.artist.add(artist_obj)


    def _get_or_create_genres(self, genres, album, primary):
        """Handle getting and creating genres."""
        for genre in genres:
            genre_obj = Genre.objects.get_or_create(**genre)[0]
            if primary:
                album.primary_genres.add(genre_obj)
            else:
                album.secondary_genres.add(genre_obj)


    def create(self, validated_data):
        """Create an album."""
        artists = validated_data.pop('artist', [])
        primary_genres = validated_data.pop('primary_genres', [])
        secondary_genres = validated_data.pop('secondary_genres', [])
        album = Album.objects.create(**validated_data, )
        self._get_or_create_artist(artists=artists, album=album)
        self._get_or_create_genres(genres=primary_genres, album=album, primary=True)
        self._get_or_create_genres(genres=secondary_genres, album=album, primary=False)

        return album

    def update(self, instance, validated_data):
        """Update an album."""
        artists = validated_data.pop('artist', None)
        primary_genres = validated_data.pop('primary_genres', None)
        secondary_genres = validated_data.pop('secondary_genres', None)

        if artists is not None:
            instance.artist.clear()
            self._get_or_create_artist(artists=artists, album=instance)
        if primary_genres is not None:
            instance.primary_genres.clear()
            self._get_or_create_genres(genres=primary_genres, album=instance, primary=True)
        if secondary_genres is not None:
            instance.secondary_genres.clear()
            self._get_or_create_genres(genres=secondary_genres, album=instance, primary=False)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class AlbumImageSerializer(serializers.ModelSerializer):
    """Serializer for uploading images to albums."""

    class Meta:
        model = Album
        fields = ['id', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': 'True'}}