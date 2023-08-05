from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from bookings.models import Booking
from config.snippets import get_tokens_for_user
from medias.models import Photo
from rooms.models import Amenity, Room
from wishlists.models import Wishlist
import pytz

asia_timezone = pytz.timezone("Asia/Seoul")


# model
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


def room_detail_url(room_id):
    return reverse("rooms:room-detail", kwargs={"room_id": room_id})


def room_review_url(room_id):
    return reverse("rooms:room-reviews", kwargs={"room_id": room_id})


def room_booking_url(room_id):
    return reverse("rooms:booking-list", kwargs={"room_id": room_id})


# === Creation Model
def create_booking(
    user,
    room,
    kind=Booking.BookingKindChoices.ROOM,
    check_in="2024-01-13",
    check_out="2024-02-15",
    experience_time="2023-07-23",
    guests=3,
):
    check_in = datetime.strptime(check_in, "%Y-%m-%d")
    check_out = datetime.strptime(check_out, "%Y-%m-%d")
    experience_time = datetime.strptime(experience_time, "%Y-%m-%d").replace(
        tzinfo=asia_timezone
    )

    return Booking.objects.create(
        user=user,
        room=room,
        kind=kind,
        check_in=check_in,
        check_out=check_out,
        experience_time=experience_time,
        guests=guests,
    )


class PublicROOMApisWithPropertyTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="password"
        )

        self.client = APIClient()

    def test_get_booking(self):
        """
        로그인 하지 않은 유저가 예약을 조회하면 성공
        """
        room = create_room(owner=self.user)
        create_booking(self.user, room)

        target_url = room_booking_url(room.id)
        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(len(res.data) > 0)

    def test_post_booking_raise_error(self):
        """
        로그인 하지 않은 유저가 새로운 예약을 생성하려 했을 때 401에러 발생
        """
        payload = {
            "check_in": "2023-07-22",
            "check_out": "2023-07-25",
            "guests": 5,
        }
        room = create_room(owner=self.user)

        target_url = room_booking_url(room.id)
        res = self.client.post(target_url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRoomApisWithPropertyTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="password"
        )

        self.client = APIClient()

        # with credentials!
        access_token, _ = get_tokens_for_user(self.user)
        self.client.force_authenticate(self.user, token=access_token)

    def test_post_booking_success(self):
        """
        인증된 유저가 새로운 예약을 요청시 성공, 201
        """
        payload = {
            "check_in": "2024-08-22",
            "check_out": "2024-08-25",
            "guests": 5,
        }
        room = create_room(owner=self.user)

        target_url = room_booking_url(room.id)
        res = self.client.post(target_url, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

    def test_post_booking_raise_error_by_room_already_exists(self):
        """
        인증된 유저가 새로운 예약을 하려고 하는데, 이미 방이 예약된 경우 400 에러
        """
        payload = {
            "check_in": "2024-01-15",
            "check_out": "2024-02-25",
            "guests": 5,
        }
        room = create_room(owner=self.user)
        create_booking(user=self.user, room=room)

        target_url = room_booking_url(room.id)
        res = self.client.post(target_url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_post_booking_raise_error_by_the_date_is_past_now(self):
        """
        인증된 유저가 새로운 예약을 하려고 하는데, 그 날짜가 현재 날짜보다 과거일 경우 400 에러
        """
        payload = {
            "check_in": "2022-01-15",
            "check_out": "2024-02-25",
            "guests": 5,
        }
        room = create_room(owner=self.user)
        create_booking(user=self.user, room=room)

        target_url = room_booking_url(room.id)
        res = self.client.post(target_url, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
