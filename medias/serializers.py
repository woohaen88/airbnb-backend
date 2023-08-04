from rest_framework import serializers

from medias.models import Photo


class RoomPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = (
            "id",
            "file",
            "description",
        )
