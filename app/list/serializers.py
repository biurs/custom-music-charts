"""
Serializers for List APIs
"""

from rest_framework import serializers

from core.models import (
    Album,
    Artist,
    List,
    Entry
)


class AlbumHelperSerializer(serializers.ModelSerializer):
    """Album Helper Serializer"""

    class Meta:
        model = Album
        fields = ['id']
        read_only_fields = ['id']


class EntrySerializer(serializers.ModelSerializer):
    """Serializers for Entries"""
    album = AlbumHelperSerializer()

    class Meta:
        model = Entry
        fields = ['album', 'description']


class ListSerializer(serializers.ModelSerializer):
    """Serializer for lists with basic info."""

    class Meta:
        model = List
        fields = ['id', 'label', 'user']
        read_only_fields = ['id', 'user']


class ListDetailSerializer(serializers.ModelSerializer):
    """Serializer for lists with detailed info."""
    albums = EntrySerializer(many=True, source='entries')

    class Meta:
        model = List
        fields = ['id', 'label', 'user', 'albums']
        read_only_fields = ['id', 'user']

    def _get_album(self, album):
        """Handle getting albums as needed."""
        return Album.objects.get(**album)

    def create(self, validated_data):
        albums_data = validated_data.pop('entries', [])
        list = List.objects.create(**validated_data)
        for entry_data in albums_data:
            album_data = entry_data.pop('album')
            album = self._get_album(album_data)
            Entry.objects.create(owner_list=list, album=album, **entry_data)

        return list

    def update(self, instance, validated_data):
        albums_data = validated_data.pop('albums')
        Entry.objects.filter(owner_list=instance).delete()
        for entry_data in albums_data:
            album_data = entry_data.pop('album')
            album = self._get_album(album_data)
            Entry.objects.create(owner_list=instance, album=album, **entry_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance