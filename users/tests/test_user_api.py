from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from common.utils import create_user

CREATE_USER_URL = reverse("users:create")
TOKEN_URL = reverse("users:token")


class PublicUserApiTest(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()

    def test_create_token_for_user(self):
        user_details = {
            "email": "test@example.com",
            "password": "testpass123",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": user_details["password"],
        }

        res = self.client.post(TOKEN_URL, payload)
        self.assertIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_create_token_bad_credentials(self):
        user_details = {
            "email": "test@example.com",
            "password": "testpass123",
        }
        create_user(**user_details)

        payload = {
            "email": user_details["email"],
            "password": "wrong_password",
        }

        res = self.client.post(TOKEN_URL, payload, format="json")
        self.assertNotIn("token", res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)


class PrivateUserApiTest(TestCase):
    def setUp(self) -> None:
        self.user = create_user(email="test@example.com", password="testpass123")
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)
