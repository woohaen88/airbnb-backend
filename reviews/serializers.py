from rest_framework import serializers

from users.serializers import TinyUserSerializer
from reviews.models import Review


class ReviewSerializer(serializers.ModelSerializer):
    user = TinyUserSerializer(read_only=True)

    class Meta:
        model = Review
        fields = (
            "id",
            "user",
            "payload",
            "rating",
        )
