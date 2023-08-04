from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

from categories.models import Category
from rooms.models import Room, Amenity
from wishlists.models import Wishlist
from wishlists.serializers import WishlistSerializer


# URL SETTING
WISHLIST_URL = reverse("wishlists:list")


def wishlist_detail_url(wishlist_id):
    return reverse("wishlists:detail", kwargs={"wishlist_id": wishlist_id})


def create_wishlist(user, name):
    return Wishlist.objects.create(name=name, user=user)


class PublicApisTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user1@example.com", password="test123!@#"
        )
        self.client = APIClient()

    def test_get_wishlist_raise_401_error(self):
        res = self.client.get(WISHLIST_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_post_wishlist_raise_401_error(self):
        payload = {"name": "wishlist_test"}

        res = self.client.post(WISHLIST_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_retrieve_wishlist_raise_401_error(self):
        wishlist = create_wishlist(self.user, "wishlist1")
        target_url = wishlist_detail_url(wishlist.id)
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_put_wishlist_raise_401_error(self):
        wishlist = create_wishlist(self.user, "wishlist1")
        target_url = wishlist_detail_url(wishlist.id)

        payload = {"name": "wishlist_test"}

        res = self.client.put(target_url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_wishlist_raise_401_error(self):
        wishlist = create_wishlist(self.user, "wishlist1")
        target_url = wishlist_detail_url(wishlist.id)

        res = self.client.delete(target_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateApisTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user1@example.com", password="test123!@#"
        )

        Amenity.objects.create(
            name="ame1",
            description="desc1",
        )

        Amenity.objects.create(
            name="ame2",
            description="desc2",
        )

        self.room_category = Category.objects.create(
            name="room_category",
            kind=Category.KindCategoryChoices.ROOMS,
        )

        self.experience_category = Category.objects.create(
            name="experience_category",
            kind=Category.KindCategoryChoices.EXPERIENCES,
        )

        self.room = Room.objects.create(
            owner=self.user,
            category=self.room_category,
            title="room1",
            country="korea",
            city="seoul",
            price=10,
            rooms=19,
            toilets=10,
            description="desc_room",
            address="address1",
            pet_friendly=True,
            kind=Room.KindChoices.PRIVATE_ROOM,
        )

        for amenity in Amenity.objects.all():
            self.room.amenities.add(amenity)

        self.client = APIClient()
        self.client.force_login(self.user)

    def test_create_wishlist_successful(self):
        payload = {"name": "wishlist_test"}

        res = self.client.post(WISHLIST_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_get_wishlist_successful(self):
        wishlist = create_wishlist(self.user, "wishlist1")
        wishlist.rooms.add(self.room)

        res = self.client.get(WISHLIST_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        wishlist = Wishlist.objects.filter(user=self.user)
        serializer = WishlistSerializer(wishlist, many=True)
        self.assertEqual(len(res.data), len(serializer.data))

    def test_retrieve_wishlist_successful(self):
        """wishlist 한개 조회"""
        wishlist = create_wishlist(self.user, "wishlist1")
        wishlist.rooms.add(self.room)
        target_url = wishlist_detail_url(wishlist.id)

        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        wishlist = Wishlist.objects.get(id=res.data["id"])
        serializer = WishlistSerializer(wishlist)
        self.assertEqual(len(res.data), len(serializer.data))

    def test_put_wishlist_successful(self):
        """wishlist 수정"""
        wishlist = create_wishlist(self.user, "wishlist1")
        wishlist.rooms.add(self.room)
        target_url = wishlist_detail_url(wishlist.id)

        # ================================================
        # name 수정
        payload = {"name": "update_name"}
        res = self.client.put(target_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # db refresh
        wishlist.refresh_from_db()

        self.assertEqual(payload["name"], wishlist.name)
        # ================================================

    def test_delete_wishlist_successful(self):
        """wishlist 삭제"""
        wishlist = create_wishlist(self.user, "wishlist1")
        wishlist.rooms.add(self.room)
        target_url = wishlist_detail_url(wishlist.id)

        res = self.client.delete(target_url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(Wishlist.objects.filter(id=wishlist.id).exists())
