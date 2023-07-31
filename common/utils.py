from django.contrib.auth import get_user_model
from django.test import TestCase

from experiences.models import Experience, Perk
from rooms.models import Room


def create_user(email: str = None, password: str = None, *args, **kwargs):
    if email is None:
        email = "test2312@example.com"
    if password is None:
        password = "test123!@#"

    return get_user_model().objects.create_user(email, password)


def create_room(owner, *args, **kwargs):
    defaults = dict(
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
    defaults.update(**kwargs)
    return Room.objects.create(owner=owner, **defaults)


def create_perk(payload=None, *args, **kwargs):
    perk_defaults = {
        "name": "name!!!",
        "details": "details!!",
        "explanation": "explanation",
    }

    perk_defaults.update(**kwargs)
    return Perk.objects.create(**perk_defaults)


def create_experience(host, *args, **kwargs):
    perk = create_perk()
    experiences_defaults = {
        "country": "한국",
        "city": "서울",
        "name": "experience_name",
        "price": 123,
        "address": "여기는 어디인가요?",
        "start": "17:20:18",
        "end": "18:21:12",
        "description": "오호호호description",
    }
    experience = Experience.objects.create(
        host=host,
        **experiences_defaults,
    )

    experience.perks.add(perk)
    return experience
