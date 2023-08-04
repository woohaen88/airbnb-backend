from django.contrib.auth import get_user_model

from rest_framework.authentication import BaseAuthentication
from common.shortcut import get_object_or_401


class TrustMeBroAuthentication(BaseAuthentication):
    def authenticate(self, request):
        username = request.headers.get("Trust-Me")
        if not username:
            return None

        user = get_object_or_401(get_user_model(), username=username)
        return (user, None)
