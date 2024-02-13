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

class ListSerializer(serializers.ModelSerializer):
    """Serializer for lists with basic info."""

    class Meta:
        model = List
        fields = ['id', 'label', 'user']
        read_only_fields = ['id', 'user']


class ListDetailSerializer(serializers.ModelSerializer):
    """Serializer for lists with detailed info."""

    class Meta:
        model = List
        fields = ['id', 'label', 'user', 'albums']

    def _get_album(self, album_id):
        """Handle getting albums as needed."""
        return Album.objects.get(id=album_id)

    def create(self, validated_data):
        albums_data = validated_data.pop('albums')
        list = List.objects.create(**validated_data)
        for entry_data in albums_data:
            album_data = entry_data.pop('album')
            album = self._get_album(album_data)
            Entry.objects.create(owned_list=list, album=album, **entry_data)

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