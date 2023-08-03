from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from common.utils import DefaultObjectCreate, create_user
from rooms.models import Room
from rooms.serializers import RoomListSerializer, RoomDetailSerializer

ROOM_URL = reverse("rooms:room-list")


def room_detail_url(room_id: int):
    return reverse("rooms:room-detail", args=(room_id,))


class PublicRoomAPisTest(TestCase):
    def setUp(self):
        self.default_object_create = DefaultObjectCreate()
        self.client = APIClient()

    def test_create_room_raise_error(self):
        """인증되지 않은 유저가 room을 생성할때 401 error 발생"""
        payload = self.default_object_create.room_defaults.copy()
        res = self.client.post(ROOM_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_room_raise_error(self):
        """인증되지 않은 유저가 room을 삭제할때 401 error 발생"""
        user1 = get_user_model().objects.create_user("user@example.com", "test123!@#")
        room = self.default_object_create.create_room(owner=user1)
        url = room_detail_url(room.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_room_other_user_raise_error(self):
        """인증된 다른 유저가 room을 삭제할때 403 error 발생"""
        user1 = create_user(email="testuser@example.com", password="test2231")
        user2 = create_user(email="user2@example.com", password="test123!@#")

        self.client.force_login(user2)

        # user1, room 생성
        room = self.default_object_create.create_room(owner=user1)
        url = room_detail_url(room.id)
        res = self.client.delete(url)

        # call API
        self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)


class PrivateRoomAPisTest(TestCase):
    """
    RoomAPITest

    TODO:
    1. GET /rooms -> 모든 rooms 데이터 조회
            result: id, name, country, city, price [v]
    2. POST /rooms -> rooms 생성
    """

    def setUp(self):
        self.default_object_create = DefaultObjectCreate()
        self.user = self.default_object_create.create_user()
        self.client = APIClient()
        self.client.force_login(self.user)

    def test_get_rooms(self):
        """
        1. GET /rooms -> 모든 rooms 데이터 조회
            result: id, name, country, city, price []
        """
        self.default_object_create.create_room(owner=self.user, title="room1")
        self.default_object_create.create_room(owner=self.user, title="room2")

        res = self.client.get(ROOM_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        # result: "id", "title", "country", "city", "price" 만조회
        target_keys = {"id", "title", "country", "city", "price"}
        for res_item in res.data:
            set_keys = set(res_item.keys())
            self.assertTrue(target_keys == set_keys)

        # data가 같은지 비교
        rooms = Room.objects.all()
        serializer = RoomListSerializer(rooms, many=True)
        self.assertEqual(res.data, serializer.data)

    def test_create_rooms_with_amenity(self):
        """2. POST /rooms -> rooms 생성"""
        payload = self.default_object_create.room_defaults.copy()
        self.default_object_create.create_category(kind="rooms")
        self.default_object_create.create_amenity(name="item1")
        self.default_object_create.create_amenity(name="item2")

        payload.update({"category": 1})
        payload.update({"amenities": [1, 2]})

        # check status code
        res = self.client.post(ROOM_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # check data
        room = Room.objects.get(id=res.data["id"])
        serializer = RoomDetailSerializer(room)
        self.assertEqual(serializer.data, res.data)

        # check authenticated user
        self.assertEqual(room.owner, self.user)

    def test_create_rooms_exclude_amenity(self):
        """3. POST /rooms -> rooms 생성"""
        payload = self.default_object_create.room_defaults.copy()
        self.default_object_create.create_category(kind="rooms")
        self.default_object_create.create_amenity(name="item1")
        self.default_object_create.create_amenity(name="item2")

        payload.update({"category": 1})

        # check status code
        res = self.client.post(ROOM_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # check data
        room = Room.objects.get(id=res.data["id"])
        serializer = RoomDetailSerializer(room)
        self.assertEqual(serializer.data, res.data)

        # check authenticated user
        self.assertEqual(room.owner, self.user)

    def test_create_rooms_partial_amenity(self):
        """3. POST /rooms -> rooms 생성"""
        payload = self.default_object_create.room_defaults.copy()
        self.default_object_create.create_category(kind="rooms")
        self.default_object_create.create_amenity(name="item1")
        self.default_object_create.create_amenity(name="item2")

        payload.update({"category": 1})
        payload.update({"amenities": [1, 3]})

        # check status code
        res = self.client.post(ROOM_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        # check data
        self.assertFalse(Room.objects.filter(id=1).exists())

    def test_create_rooms_experience_category_raise_error(self):
        """room 생성시 experiences category를 넣으면 error"""
        self.default_object_create.create_category(kind="experiences")
        payload = self.default_object_create.room_defaults.copy()
        payload.update({"category": 1})

        res = self.client.post(ROOM_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
