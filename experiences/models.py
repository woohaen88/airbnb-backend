from django.conf import settings
from django.db import models

from common.models import CommonModel


class Experience(CommonModel):
    country = models.CharField(
        max_length=20,
    )
    city = models.CharField(
        max_length=20,
    )
    name = models.CharField(
        max_length=140,
    )
    price = models.PositiveIntegerField()
    address = models.TextField()
    start = models.TimeField()
    end = models.TimeField()
    description = models.TextField()

    host = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="experiences",
    )

    perks = models.ManyToManyField(
        "experiences.Perk",
    )

    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )

    def __str__(self):
        return self.name


class Perk(CommonModel):
    name = models.CharField(
        max_length=100,
    )
    details = models.CharField(
        max_length=255,
        blank=True,
        default="",
    )
    explanation = models.TextField(
        blank=True,
        default="",
    )

    def __str__(self):
        return self.name
