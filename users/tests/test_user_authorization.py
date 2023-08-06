from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status

from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


ME_URL = reverse("users:me")


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return str(refresh.access_token), str(refresh)


def create_user(email="test@example.com", password="test123!@#"):
    return get_user_model().objects.create_user(email, password)


class PublicUserAuthorizationTest(TestCase):
    def setUp(self):
        self.user = create_user()
        self.client = APIClient()

    def test_me_get_raise_401_error(self):
        """인증되지 않은 유저가 get 요청시 /api/v1/users/me 접근하면 401error"""
        res = self.client.get(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_me_put_raise_401_error(self):
        """인증되지 않은 유저가 put 요청시 /api/v1/users/me 접근하면 401error"""
        res = self.client.put(ME_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserAuthorizationTest(TestCase):
    def setUp(self):
        self.user = create_user()
        token, _ = get_tokens_for_user(self.user)
        self.client = APIClient()
        self.client.force_authenticate(self.user, token=token)

    def test_me_get_success(self):
        """인증되지 않은 유저가 get 요청시 /api/v1/users/me 접근하면 200"""
        res = self.client.get(ME_URL)
        excepts = (
            "password",
            "is_superuser",
            "id",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
        )
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for param in excepts:
            self.assertNotIn(param, res.data)

    def test_me_put_success(self):
        """인증되지 않은 유저가 put 요청시 /api/v1/users/me 접근하면 401error"""
        excepts = (
            "password",
            "is_superuser",
            "id",
            "is_staff",
            "is_active",
            "groups",
            "user_permissions",
        )
        payload = {
            "username": "update_username",
        }
        res = self.client.put(ME_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        for param in excepts:
            self.assertNotIn(param, res.data)

        self.user.refresh_from_db()

        self.assertEqual(self.user.username, payload["username"])
