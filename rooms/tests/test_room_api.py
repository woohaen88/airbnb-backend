from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from common.utils import DefaultObjectCreate, create_user
from reviews.serializers import ReviewSerializer
from rooms.models import Room
from rooms.serializers import RoomListSerializer, RoomDetailSerializer

ROOM_URL = reverse("rooms:room-list")


def room_detail_url(room_id: int):
    return reverse("rooms:room-detail", args=(room_id,))


def room_review_url(room_id: int, page=None):
    return reverse("rooms:room-reviews", args=(room_id,))


class PublicRoomAPisTest(TestCase):
    def setUp(self):
        self.default_object_create = DefaultObjectCreate()
        self.client = APIClient()
        self.user = create_user(email="test@test.com", password="password123")

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

    def test_update_room_raise_error(self):
        """인증되지 않은 유저가 room을 수정할때 401 error 발생"""
        user1 = get_user_model().objects.create_user("user@example.com", "test123!@#")
        room = self.default_object_create.create_room(owner=user1)

        target_url = room_detail_url(room.id)
        res = self.client.put(target_url)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_room_reviews(self):
        room = self.default_object_create.create_room(owner=self.user)
        experience = self.default_object_create.create_experience(host=self.user)

        self.default_object_create.create_review(
            user=self.user,
            room=room,
            experience=experience,
            payload="review1",
            rating=3,
        )

        url = room_review_url(room.id)
        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        room = Room.objects.get(id=room.id)
        serializer = ReviewSerializer(room.reviews.all(), many=True)

        self.assertEqual(serializer.data, res.data)

    def test_get_room_reviews_with_pagination(self):
        room = self.default_object_create.create_room(owner=self.user)
        experience = self.default_object_create.create_experience(host=self.user)

        for i in range(10):
            self.default_object_create.create_review(
                user=self.user,
                room=room,
                experience=experience,
                payload="review1",
                rating=3,
            )

        for page in range(1, 5):
            url = f"/api/v1/rooms/{room.id}/reviews/?page={page}"
            res = self.client.get(url)
            self.assertEqual(res.status_code, status.HTTP_200_OK)
            if page != 4:
                self.assertEqual(len(res.data), 3)
            else:
                self.assertEqual(len(res.data), 1)


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
        self.client.force_authenticate(self.user)
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

        # data가 같은지 비교
        rooms = Room.objects.all()
        serializer = RoomListSerializer(rooms, many=True)

        # 동적 필드 제거
        # is_owner = res.data[0].pop("is_owner")
        #
        # serializer.data[0].pop("is_owner")
        # self.assertTrue(is_owner)  # 작성자가 같은지 비교
        # self.assertEqual(res.data[0], serializer.data[0])

    def test_get_room_exact_fields(self):
        """매칠되는 필드만 조회"""
        room = self.default_object_create.create_room(owner=self.user)
        experience = self.default_object_create.create_experience(host=self.user)

        self.default_object_create.create_review(
            user=self.user,
            room=room,
            experience=experience,
            payload="review1",
            rating=3,
        )

        url = room_detail_url(room.id)
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        target_keys = [
            "reviews",
        ]
        for key in target_keys:
            self.assertIn(key, res.data)

    def test_create_rooms_with_amenity(self):
        """2. POST /rooms -> rooms 생성"""
        payload = self.default_object_create.room_defaults.copy()
        self.default_object_create.create_category(kind="rooms")
        self.default_object_create.create_amenity(name="item1")
        self.default_object_create.create_amenity(name="item2")

        payload.update({"category": 1})
        payload.update({"amenities": [1, 2]})

        # check status code
        res = self.client.post(ROOM_URL, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        # check data
        room = Room.objects.get(id=res.data["id"])
        serializer = RoomDetailSerializer(room)

        # 동적 필드가 있으면 제외해야함
        serializer_data = serializer.data
        dynamic_fields = ["is_owner"]
        for dynamic_field in dynamic_fields:
            serializer_data.pop(dynamic_field)
            is_owner_by_api = res.data.pop(dynamic_field)
            self.assertTrue(is_owner_by_api)

        self.assertEqual(serializer_data, res.data)

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

        # 동적 필드가 있으면 제외해야함
        serializer_data = serializer.data
        dynamic_fields = ["is_owner"]
        for dynamic_field in dynamic_fields:
            serializer_data.pop(dynamic_field)
            is_owner_by_api = res.data.pop(dynamic_field)
            self.assertTrue(is_owner_by_api)

        self.assertEqual(serializer_data, res.data)

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

    # delete
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

    ### update
    # 인증된 다른 유저가 수정하려할 때 에러 발생
    # 인증된 같은 유저가 올바르게 수정하면 성공
    # 인증된 같은 유저가 invalid 값을 넣으면 400 error
    def test_update_room_by_other_user_raise_error(self):
        """인증된 다른 유져가 수정하려할 때 에러발생"""
        other_user = create_user(email="other@example.com", password="test123!@#")
        self.default_object_create.create_room(owner=other_user)

        room = Room.objects.get(owner=other_user)
        target_url = room_detail_url(room.id)

        payload = {"title": "update title"}

        res = self.client.put(target_url, payload, format="json")

        self.assertEqual(
            res.status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_update_room_correctly(self):
        """인증된 같은 유저가 올바르게 수정하면 성공"""
        self.default_object_create.create_room(owner=self.user)

        room = Room.objects.get(owner=self.user)
        target_url = room_detail_url(room.id)

        payload = {"title": "update title"}

        res = self.client.put(target_url, payload, format="json")

        self.assertEqual(
            res.status_code,
            status.HTTP_200_OK,
        )

        room.refresh_from_db()
        serializer = RoomDetailSerializer(room)

        self.assertEqual(payload["title"], room.title)

        # 동적 필드가 있으면 제외해야함
        serializer_data = serializer.data

        dynamic_fields = ["is_owner"]
        for dynamic_field in dynamic_fields:
            serializer_data.pop(dynamic_field)
            is_owner_by_api = res.data.pop(dynamic_field)
            self.assertTrue(is_owner_by_api)

        self.assertEqual(serializer_data, res.data)

    def test_update_room_invalid_raise_error(self):
        """인증된 같은 유저가 invalid 값을 넣으면 400 error"""
        self.default_object_create.create_room(owner=self.user)
        self.default_object_create.create_amenity(name="item1")

        # 없는 카테고리로 수정할 경우 -> 400error
        room = Room.objects.get(owner=self.user)
        target_url = room_detail_url(room.id)
        payload = {"category": 100}
        res = self.client.put(target_url, payload, format="json")

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        before_serializer = RoomDetailSerializer(room)
        room.refresh_from_db()
        after_serializer = RoomDetailSerializer(room)
        self.assertEqual(before_serializer.data, after_serializer.data)

        # 없는 amenities만 있을 경우 -> 400error, room도 수정되면 안됨
        room = Room.objects.get(owner=self.user)
        target_url = room_detail_url(room.id)
        payload = {"amenities": [100, 200, 300]}
        res = self.client.put(target_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        before_serializer = RoomDetailSerializer(room)
        room.refresh_from_db()
        after_serializer = RoomDetailSerializer(room)
        self.assertEqual(before_serializer.data, after_serializer.data)

        # 없는 amenities가 일부분 있을 경우 -> 400error, room도 수정되면 안됨
        room = Room.objects.get(owner=self.user)
        target_url = room_detail_url(room.id)
        payload = {"amenities": [1, 200, 300]}
        res = self.client.put(target_url, payload, format="json")
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

        before_serializer = RoomDetailSerializer(room)
        room.refresh_from_db()
        after_serializer = RoomDetailSerializer(room)
        self.assertEqual(before_serializer.data, after_serializer.data)
