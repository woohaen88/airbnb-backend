from django.contrib.auth import get_user_model

from rest_framework.authentication import BaseAuthentication
from common.shortcut import get_object_or_401
from rest_framework_simplejwt.authentication import JWTAuthentication


class TrustMeBroAuthentication(BaseAuthentication):
    def authenticate(self, request):
        username = request.headers.get("Trust-Me")
        if not username:
            return None

        user = get_object_or_401(get_user_model(), username=username)
        return (user, None)


class SimpleJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        raw_token = request.COOKIES.get("access_token")
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)

        return self.get_user(validated_token), validated_token
