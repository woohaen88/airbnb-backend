from django.db import models

from common.models import CommonModel
from config import settings


class Room(CommonModel):
    class KindChoices(models.TextChoices):
        ENTIRE_PLACE = "entire_place", "Entire Place"
        PRIVATE_ROOM = "private_room", "Private Room"
        SHARED_ROOM = "shared_room", "Shared Room"

    title = models.CharField(
        max_length=150,
    )
    country = models.CharField(
        max_length=10,
    )
    city = models.CharField(
        max_length=20,
    )
    price = models.PositiveIntegerField()
    rooms = models.PositiveIntegerField()
    toilets = models.PositiveIntegerField()
    description = models.TextField()
    address = models.CharField(
        max_length=150,
    )
    pet_friendly = models.BooleanField(
        blank=True,
    )
    kind = models.CharField(
        max_length=15,
        choices=KindChoices.choices,
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )

    amenities = models.ManyToManyField(
        "rooms.Amenity",
        blank=True,
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        auto_now=True,
    )

    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def total_amenities(self):
        return self.amenities.count()

    def __str__(self):
        return self.title


class Amenity(CommonModel):
    name = models.CharField(max_length=150)
    description = models.CharField(
        max_length=150,
        null=True,
        blank=True,
    )

    class Meta:
        verbose_name_plural = "amenities"

    def __str__(self):
        return self.name
