from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin


@admin.register(get_user_model())
class UserAdmin(UserAdmin):
    fieldsets = [
        (
            "Profile",
            {
                "fields": [
                    "avatar",
                    "email",
                    "password",
                    "username",
                    "is_host",
                    "gender",
                    "language",
                    "currency",
                ],
                "classes": ("wide",),
            },
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ("collapse",),
            },
        ),
        (
            "Important dates",
            {
                "fields": (
                    "last_login",
                    "date_joined",
                ),
                "classes": ("collapse",),
            },
        ),
    ]

    list_display = (
        "email",
        "username",
        "is_host",
    )
