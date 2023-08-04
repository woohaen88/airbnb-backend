from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from rooms.models import Room, Amenity
from wishlists.models import Wishlist


def create_room(
    owner,
    amenities=False,
    title="room_title",
    country="korea",
    city="seoul",
    price=123,
    rooms=3,
    toilets=3,
    description="desc1",
    address="address",
    pet_friendly=True,
    kind=Room.KindChoices.PRIVATE_ROOM,
):
    room = Room.objects.create(
        owner=owner,
        title=title,
        country=country,
        city=city,
        price=price,
        rooms=rooms,
        toilets=toilets,
        description=description,
        address=address,
        pet_friendly=pet_friendly,
        kind=kind,
    )
    if amenities:
        amen1 = Amenity.objects.create(name="amen1", description="desc1")
        amen2 = Amenity.objects.create(name="amen2", description="desc2")

        room.amenities.add(amen1, amen2)
        return room

    return room


def create_wishlist(
    user,
    name="wishlist1",
):
    return Wishlist.objects.create(
        user=user,
        name=name,
    )


def wishlist_toggle_url(wishlist_id, room_id):
    return reverse(
        "wishlists:wishlist-toggle",
        kwargs={
            "wishlist_id": wishlist_id,
            "room_id": room_id,
        },
    )


def wishlist_detail_url(wishlist_id):
    return reverse("wishlists:detail", args=(wishlist_id,))


class PublicWishlistWithSomeActionTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="test123!@3"
        )

    def test_put_toggle_insert_room_of_wishlist(self):
        """401 error"""
        wishlist = create_wishlist(self.user)
        room = create_room(self.user, amenities=True)

        target_url = wishlist_toggle_url(wishlist.id, room.id)
        res = self.client.put(target_url)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateWishlistWithSomeActionTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="test@example.com", password="test123!@3"
        )
        self.client.force_login(self.user)

    def test_put_toggle_insert_room_of_wishlist(self):
        """wishlist가 생성된 상태에서 put 메소드로 룸 생성 및 삭제"""
        wishlist = create_wishlist(self.user)

        # 처음에 wishlist에 룸은 빈값
        target_url = wishlist_detail_url(wishlist.id)
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["rooms"]), 0)

        # put 메소드 -> 추가
        room = create_room(self.user, amenities=True)
        target_url = wishlist_toggle_url(wishlist.id, room.id)
        res = self.client.put(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        wishlist.refresh_from_db()
        target_url = wishlist_detail_url(wishlist.id)
        res = self.client.get(target_url)
        self.assertEqual(len(res.data["rooms"]), 1)

        # put 메소드 -> 삭제
        target_url = wishlist_toggle_url(wishlist.id, room.id)
        res = self.client.put(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        wishlist.refresh_from_db()
        target_url = wishlist_detail_url(wishlist.id)
        res = self.client.get(target_url)
        self.assertEqual(len(res.data["rooms"]), 0)
