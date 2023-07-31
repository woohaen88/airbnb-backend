from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    class GenderChoices(models.TextChoices):
        MALE = ("male", "Male")  # value for database / value for admin page
        FEMALE = "female", "Female"

    class LanguageChoices(models.TextChoices):
        KR = "kr", "Korean"
        EN = "en", "English"

    class CurrencyChoices(models.TextChoices):
        WON = "won", "Korean Won"
        USD = "usd", "Dollar"

    first_name = models.CharField(
        max_length=150,
        editable=False,
    )
    last_name = models.CharField(
        max_length=150,
        editable=False,
    )
    name = models.CharField(
        max_length=150,
    )
    is_host = models.BooleanField(
        null=True,
    )

    avatar = models.ImageField(
        blank=True,
    )

    gender = models.CharField(
        max_length=10,
        choices=GenderChoices.choices,
    )

    language = models.CharField(
        max_length=2,
        choices=LanguageChoices.choices,
    )

    currency = models.CharField(
        max_length=3,
        choices=CurrencyChoices.choices,
    )
