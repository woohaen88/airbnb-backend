from rest_framework.serializers import ModelSerializer

from rooms.models import Amenity, Room

from users.serializers import TinyUserSerializer
from categories.serializers import CategorySerializer


class AmenitySerializer(ModelSerializer):
    class Meta:
        model = Amenity
        fields = "__all__"


class RoomDetailSerializer(ModelSerializer):
    owner = TinyUserSerializer(read_only=True)
    amenities = AmenitySerializer(read_only=True, many=True, required=False)
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Room
        fields = "__all__"

    def create(self, validated_data):
        return Room.objects.create(**validated_data)


class RoomListSerializer(ModelSerializer):
    class Meta:
        model = Room
        fields = (
            "id",
            "title",
            "country",
            "city",
            "price",
        )
