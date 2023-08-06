from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, AbstractUser
from django.db import models


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_field):
        if not email:
            raise ValueError("User must have an email address.")
        if extra_field.get("name", None) is None:
            name = email.split("@")[0]
        else:
            name = extra_field.pop("name")
        user = self.model(
            email=self.normalize_email(email),
            username=name,
            **extra_field,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        """create and return a new superuser"""
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    email = models.EmailField(
        verbose_name="email address",
        unique=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []
    objects = UserManager()

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
    username = models.CharField(
        max_length=150,
    )
    is_host = models.BooleanField(
        null=True,
    )

    avatar = models.URLField(
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

    def __str__(self):
        return self.username
