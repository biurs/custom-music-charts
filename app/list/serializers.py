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

from album.serializers import AlbumSerializer as AlbumDetailSerializer


class EntryDetailSerializer(serializers.ModelSerializer):
    """Serializers for Creating Entries"""
    album = AlbumDetailSerializer()

    class Meta:
        model = Entry
        fields = ['album', 'description']


class ListDetailSerializer(serializers.ModelSerializer):
    """Serializer Creating or updating lists."""
    albums = EntryDetailSerializer(many=True, source='entries')

    class Meta:
        model = List
        fields = ['id', 'label', 'user', 'albums']
        read_only_fields = ['id', 'user']


class AlbumHelperSerializer(serializers.ModelSerializer):
    """Album Helper Serializer"""

    class Meta:
        model = Album
        fields = ['id']


class EntrySerializer(serializers.ModelSerializer):
    """Serializer for Entries getting"""
    album = serializers.PrimaryKeyRelatedField(queryset=Album.objects.all())

    class Meta:
        model = Entry
        fields = ['album', 'description']


class ListSerializer(serializers.ModelSerializer):
    """Serializer for lists with basic info."""
    albums = EntrySerializer(many=True, source='entries')

    class Meta:
        model = List
        fields = ['id', 'label', 'user', 'albums']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        albums_data = validated_data.pop('entries', [])
        list = List.objects.create(**validated_data)
        for entry_data in albums_data:
            album_data = entry_data.pop('album')
            Entry.objects.create(owner_list=list, album=album_data, **entry_data)
        return list

    def update(self, instance, validated_data):
        albums_data = validated_data.pop('entries', [])
        Entry.objects.filter(owner_list=instance).delete()
        for entry_data in albums_data:
            album_data = entry_data.pop('album')
            Entry.objects.create(owner_list=instance, album=album_data, **entry_data)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
