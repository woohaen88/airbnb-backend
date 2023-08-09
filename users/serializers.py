from django.contrib.auth import get_user_model, authenticate
from rest_framework import serializers
from rest_framework import status
from rest_framework.exceptions import ParseError
from rest_framework.serializers import ModelSerializer, Serializer


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


class UserLogoutSerializer(Serializer):
    pass


class PrivateUserSerializer(ModelSerializer):
    class Meta:
        model = get_user_model()
        exclude = (
            "password",
            "is_superuser",
            "id",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
        )


class PasswordChangeSerializer(serializers.ModelSerializer):
    raw_password = serializers.CharField(style={"input_type": "password"})
    change_password = serializers.CharField(style={"input_type": "password"})

    class Meta:
        model = get_user_model()
        fields = ("raw_password", "change_password")
        extra_kwargs = {
            "change_password": {
                "write_only": True,
            },
            "raw_password": {
                "write_only": True,
            },
        }

    def validate(self, attrs):
        raw_password = attrs.get("raw_password")
        request = self.context.get("request")
        user = request.user

        if not user.check_password(raw_password):
            raise ParseError("저기여 비밀번호를 틀리면 오또케")

        return attrs

    def update(self, instance, validated_data):
        validated_data.pop("raw_password")
        change_password = validated_data.pop("change_password")

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.set_password(change_password)
        instance.save()

        return instance


class SocialLocalSerializer(serializers.Serializer):
    pass
