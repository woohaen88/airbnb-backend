from django.conf import settings
from django.db import models

from common.models import CommonModel


class Wishlist(CommonModel):
    """Wishlist Model Definition"""

    name = models.CharField(
        max_length=150,
    )
    rooms = models.ManyToManyField(
        "rooms.Room",
    )

    experiences = models.ManyToManyField(
        "experiences.Experience",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="wishlists",
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "wishlist"
