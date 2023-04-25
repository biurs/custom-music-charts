"""
Serializers for the list APIs.
"""
from rest_framework import serializers

from core.models import List

class ListSerializer(serializers.ModelSerializer):
    """Serializer for artists."""

    class Meta:
        model = List
        fields = ['name', 'description', 'owner']
        read_only_fields = ['id']