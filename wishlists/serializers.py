from rest_framework import serializers

from rooms.serializers import RoomListSerializer
from wishlists.models import Wishlist


class WishlistSerializer(serializers.ModelSerializer):
    rooms = RoomListSerializer(read_only=True, many=True)

    class Meta:
        model = Wishlist
        fields = (
            "id",
            "name",
            "rooms",
        )


class WishlistToggleSerializer(serializers.Serializer):
    pass
