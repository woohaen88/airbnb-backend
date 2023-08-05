from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from config.snippets import get_tokens_for_user
from medias.models import Photo
from rooms.models import Amenity, Room
from wishlists.models import Wishlist

BOOKING_URL = reverse("rooms:booking-list")


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


class PublicROOMApisWithPropertyTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="password"
        )

        self.room_photo = Photo.objects.create(
            file="http://example.com",
            description="desc1",
            room=self.room,
        )

        self.experiece_photo = Photo.objects.create(
            file="http://example_experience.com",
            description="desc2",
            experience=self.experience,
        )

        self.client = APIClient()

    def test_post_booking_raise_error(self):
        """
        로그인 하지 않은 유저가 새로운 예약을 생성하려 했을 때 401에러 발생
        """
        pass


class PrivateRoomApisWithPropertyTest(TestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            email="user@example.com", password="password"
        )

        self.room_photo = Photo.objects.create(
            file="http://example.com",
            description="desc1",
            room=self.room,
        )

        self.experiece_photo = Photo.objects.create(
            file="http://example_experience.com",
            description="desc2",
            experience=self.experience,
        )

        self.client = APIClient()

        # with credentials!
        access_token, _ = get_tokens_for_user(self.user)
        self.client.force_authenticate(self.user, token=access_token)

    def test_post_booking_success(self):
        """
        인증된 유저가 새로운 예약을 요청시 성공, 201
        """
        pass

    def test_post_booking_raise_error_by_blabla1(self):
        """
        인증된 유저가 새로운 예약을 하려고 하는데, 이미 방이 예약된 경우 에러발생? 에러코드 미상
        """
        pass

    def test_post_booking_raise_error_by_blabla2(self):
        """
        인증된 유저가 새로운 예약을 하려고 하는데, 그 날짜가 현재 날짜보다 미래일 경우 에러
        에러코드 미상
        """
        pass

    def test_post_booking_raise_error_by_blabla3(self):
        """
        인증된 유저가 새로운 예약을 하려고 하는데, 그 날짜가 현재 날짜보다 과거일 경우 에러
        에러코드 미상
        """
        pass
