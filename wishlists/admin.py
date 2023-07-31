from django.contrib import admin

from wishlists.models import Wishlist


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        # "rooms",
        # "experiences",
        "user",
    )
