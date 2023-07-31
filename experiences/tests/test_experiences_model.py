from django.contrib.auth import get_user_model
from django.test import TestCase
from experiences.models import Experience, Perk
from django.db import IntegrityError


class ExperiencesTest(TestCase):
    """
    TODO:
    1. start < end []
    2. price: positive Integer -> 음수가 들어오면 error [v]
    3. experience모델 object는 name과 같아야함 [v]
    4. perk모델 object는 name과 같아야함 [v]
    5. experience모델과 perk모델은 MtoM으로 연결되어야함 [v]
    6. categories 속성이 존재하는가? [v]
    """

    def setUp(self) -> None:
        self.experiences_defaults = {
            "country": "한국",
            "city": "서울",
            "name": "experience_name",
            "price": 123,
            "address": "여기는 어디인가요?",
            "start": "17:20:18",
            "end": "18:21:12",
            "description": "오호호호description",
        }

        self.perk_defaults = {
            "name": "name!!!",
            "details": "details!!",
            "explanation": "explanation",
        }

        self.user = get_user_model().objects.create_user(
            "test@example.com", "test123!@#"
        )

    def test_create_experiences_model(self):
        """
        model creation Test
        3. experience모델 object는 name과 같아야함
        """
        experiences_defaults_copy = self.experiences_defaults.copy()
        experience = Experience.objects.create(
            host=self.user,
            **experiences_defaults_copy,
        )

        self.assertEqual(experience.name, str(experience))

    def test_create_perk_model(self):
        """
        model creation Test
        4. perk모델 object는 name과 같아야함
        """
        perk_defaults_copy = self.perk_defaults.copy()
        perk = Perk.objects.create(
            **perk_defaults_copy,
        )

        self.assertEqual(perk.name, str(perk))

    def test_experience_model_and_perk_model_with_mtom(self):
        """5. experience모델과 perk모델은 MtoM으로 연결되어야함"""
        perk_defaults_copy = self.perk_defaults.copy()
        perk = Perk.objects.create(
            **perk_defaults_copy,
        )

        experiences_defaults_copy = self.experiences_defaults.copy()
        experience = Experience.objects.create(
            host=self.user,
            **experiences_defaults_copy,
        )

        experience.perks.add(perk)

    def test_experience_price_negative_value_return_error(self):
        """2. price: positive Integer -> 음수가 들어오면 error"""
        experiences_defaults_copy = self.experiences_defaults.copy()
        experiences_defaults_copy.update({"price": -12})

        with self.assertRaises(IntegrityError):
            experience = Experience.objects.create(
                host=self.user,
                **experiences_defaults_copy,
            )

    def test_category_isin_experiences(self):
        experiences_defaults_copy = self.experiences_defaults.copy()
        experience = Experience.objects.create(
            host=self.user,
            **experiences_defaults_copy,
        )

        self.assertTrue(hasattr(experience, "category"))
