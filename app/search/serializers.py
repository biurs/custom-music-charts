from rest_framework import serializers

from core.models import Artist, Album

class SearchSerializer(serializers.BaseSerializer):
    """Serializer for artists."""
    def to_representation(self, instance):
        if isinstance(instance, Artist):
            return {
                'name': instance.name,
                'id': instance.id,
                'start_year': instance.start_year,
                'end_year': instance.end_year,
            }
        if isinstance(instance, Album):
            return {
                'title': instance.title,
                'id': instance.id,
            }
        # similarity = serializers.FloatField()
        # id = serializers.IntegerField()
        # name = serializers.CharField()
        # start_year = serializers.IntegerField()
        # end_year = serializers.IntegerField()


    # class Meta:
    #     fields = ['name', 'origin_country', 'start_year', 'end_year', 'similarity']
    #     read_only_fields = ['id']