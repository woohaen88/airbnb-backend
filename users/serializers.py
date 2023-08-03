from django.contrib.auth import get_user_model, authenticate
from rest_framework.authtoken.models import Token

from rest_framework.serializers import ModelSerializer, Serializer
from rest_framework import serializers
from rest_framework import status


class TinyUserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "username",
            "avatar",
            "email",
        )


class UserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = (
            "email",
            "password",
            "username",
        )


class AuthTokenSerializer(Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(
        style={
            "input_type": "password",
        },
        trim_whitespace=False,
    )

    def validate(self, attrs):
        """attrs <- request.data"""
        email = attrs.get("email")
        password = attrs.get("password")
        user = authenticate(
            request=self.context.get("request"),
            username=email,
            password=password,
        )
        if not user:
            msg = "Unable to authenticate with provided credentials"
            raise serializers.ValidationError(msg, code=status.HTTP_401_UNAUTHORIZED)

        attrs["user"] = user
        return attrs
