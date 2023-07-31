from django.test import TestCase

from common.utils import DefaultObjectCreate
from wishlists.models import Wishlist


class WishlistTest(TestCase):
    def setUp(self) -> None:
        defaultObjectCreate = DefaultObjectCreate()
        self.user = defaultObjectCreate.create_user()
        self.room = defaultObjectCreate.create_room(owner=self.user)
        self.experience = defaultObjectCreate.create_experience(host=self.user)

    def test_wishlist_model(self):
        wishlist = Wishlist.objects.create(
            name="wishlist_test",
            user=self.user,
        )

        self.assertTrue(hasattr(wishlist, "rooms"))
        self.assertTrue(hasattr(wishlist, "experiences"))

        self.assertEqual(wishlist._meta.verbose_name_plural, "wishlist")
        self.assertEqual(wishlist.name, str(wishlist))
