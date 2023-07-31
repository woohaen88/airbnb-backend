from django.contrib.auth import get_user_model
from django.test import TestCase


def create_user(**params):
    """create and return a new user"""
    defaults = {
        "email": "test@example.com",
        "password": "testpass123",
    }

    defaults.update(params)
    return get_user_model().objects.create_user(**defaults)


class UserModelTest(TestCase):
    def test_create_user_with_email_successful(self):
        """
        1. email로 유저 생성
        2. password validator
        """
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))
        self.assertEqual(user.name, str(user))

    def test_create_user_with_email_raises_error(self):
        """email이 없으면 error"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "test123!@#")

    # def test_create_user_and_right_values(self):
    #     user = create_user()

    def test_create_superuser(self):
        """superuser Test"""
        user = get_user_model().objects.create_superuser(
            "test@example.com", "test123!@#"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)
