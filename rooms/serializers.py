from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from categories.serializers import CategorySerializer
from medias.serializers import PhotoSerializer
from reviews.serializers import ReviewSerializer
from rooms.models import Amenity, Room
from users.serializers import TinyUserSerializer
from wishlists.models import Wishlist
from medias.serializers import PhotoSerializer


class AmenitySerializer(ModelSerializer):
    class Meta:
        model = Amenity
        fields = "__all__"


class RoomDetailSerializer(ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    owner = TinyUserSerializer(read_only=True)
    amenities = AmenitySerializer(read_only=True, many=True, required=False)
    category = CategorySerializer(read_only=True)

    rating = serializers.SerializerMethodField()
    reviews = ReviewSerializer(
        many=True,
        read_only=True,
    )
    photos = PhotoSerializer(read_only=True, many=True)
    is_liked = serializers.SerializerMethodField()

    class Meta:
        model = Room
        fields = (
            "id",
            "title",
            "country",
            "city",
            "price",
            "rooms",
            "toilets",
            "description",
            "address",
            "pet_friendly",
            "kind",
            "owner",
            "amenities",
            "created_at",
            "updated_at",
            "category",
            "total_amenities",
            "rating",
            "is_owner",
            "reviews",
            "photos",
            "is_liked",
        )

    def get_is_liked(self, room: Room):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Wishlist.objects.filter(
                user=request.user, rooms__id=room.id
            ).exists()
        return False

    def get_is_owner(self, room: Room):
        request = self.context.get("request")
        if request:
            return room.owner == request.user
        return False

    def create(self, validated_data):
        return Room.objects.create(**validated_data)

    def get_rating(self, room: Room):
        return room.rating()


class RoomListSerializer(ModelSerializer):
    is_owner = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()
    photos = PhotoSerializer(many=True)

    class Meta:
        model = Room
        fields = (
            "id",
            "title",
            "country",
            "city",
            "price",
            "rating",
            "is_owner",
            "photos",
        )

    def get_rating(self, room: Room):
        return room.rating()

    def get_is_owner(self, room: Room):
        if self.context.get("request", False):
            request = self.context["request"]
            return room.owner == request.user
        return False
