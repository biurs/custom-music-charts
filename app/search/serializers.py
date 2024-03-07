from rest_framework import serializers

from core.models import Artist, Album, List, Genre

class SearchSerializer(serializers.BaseSerializer):
    """Serializer for artists."""
    def to_representation(self, instance):
        if isinstance(instance, Artist):
            returndict = {
                'type': 'artist',
                'name': instance.name,
                'id': str(instance.id),
                'start_year': instance.start_year,
                'end_year': instance.end_year,
            }
            if (instance.albums.exists()):
                image = instance.albums.exists().image.url
                returndict['image'] = image
            return returndict
        if isinstance(instance, Album):
            genrelist = []
            for genre in instance.primary_genres.all():
                genrelist.append([genre.id, genre.name])
            return {
                'type': 'album',
                'title': instance.title,
                'id': str(instance.id),
                'artist_name': instance.artist.first().name,
                'artist_id': instance.artist.first().id,
                'release_date': instance.release_date,
                'genrelist': genrelist,
                'image': instance.image.url,
            }
        if isinstance(instance, List):
            imagelist = []
            for album in instance.albums.order_by('id')[:4]:
                if album.image.url:
                    imagelist.append(album.image.url)
            return {
                'type': 'list',
                'label': instance.label,
                'id': str(instance.id),
                'user_name': instance.user.name,
                'user_id': instance.user.id,
                'imagelist': imagelist
            }
        if isinstance(instance, Genre):
            return {
                'type': 'genre',
                'name': instance.name,
                'description': instance.description,
                'id': str(instance.id)
            }
        # similarity = serializers.FloatField()
        # id = serializers.IntegerField()
        # name = serializers.CharField()
        # start_year = serializers.IntegerField()
        # end_year = serializers.IntegerField()


    # class Meta:
    #     fields = ['name', 'origin_country', 'start_year', 'end_year', 'similarity']
    #     read_only_fields = ['id']