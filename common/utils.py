import django.db.utils
from django.contrib.auth import get_user_model
from django.test import TestCase

from experiences.models import Experience, Perk
from rooms.models import Room, Amenity


class DefaultObjectCreate:
    def __init__(self):
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
        self.room_defaults = dict(
            title="title",
            country="한국",
            city="서울",
            price=123012,
            rooms=2,
            toilets=3,
            description="description",
            address="address",
            pet_friendly=True,
            kind="entire_place",
        )

    def create_user(self, email: str = None, password: str = None, *args, **kwargs):
        if email is None:
            email = "test2312@example.com"
        if password is None:
            password = "test123!@#"

        try:
            user = get_user_model().objects.create_user(email, password)
        except django.db.utils.IntegrityError:
            raise ValueError("User가 중복됩니다.")
        else:
            return user
        # return get_user_model().objects.create_user(email, password)

    def create_room(self, owner, *args, **kwargs):
        room_defaults_copy = self.room_defaults.copy()
        room_defaults_copy.update(**kwargs)
        return Room.objects.create(owner=owner, **room_defaults_copy)

    def create_perk(self, payload=None, *args, **kwargs):
        perk_defaults_copy = self.perk_defaults.copy()
        perk_defaults_copy.update(**kwargs)
        return Perk.objects.create(**perk_defaults_copy)

    def create_experience(self, host, *args, **kwargs):
        perk = self.create_perk()
        experiences_defaults_copy = self.experiences_defaults.copy()
        experiences_defaults_copy.update(**kwargs)
        experience = Experience.objects.create(
            host=host,
            **experiences_defaults_copy,
        )

        experience.perks.add(perk)
        return experience

    def create_amenity(self, *args, **kwargs):
        return Amenity.objects.create(**kwargs)
