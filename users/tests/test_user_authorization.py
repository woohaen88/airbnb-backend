from django.test import TestCase
from django.urls import reverse


ME_URL = reverse("users:me")


class UserAuthorizationTest(TestCase):
    def setUp(self):
        pass
