from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status


from common.utils import create_user, DefaultObjectCreate
from medias.models import Photo
from reviews.models import Review
from reviews.serializers import ReviewSerializer

generator = DefaultObjectCreate()


def room_detail_url(room_id):
    return reverse("rooms:room-detail", kwargs={"room_id": room_id})


def room_review_url(room_id):
    return reverse("rooms:room-reviews", kwargs={"room_id": room_id})


class PublicROOMApisWithPropertyTest(TestCase):
    def setUp(self):
        self.user = create_user(email="user@example.com", password="password")
        self.room = generator.create_room(owner=self.user)
        self.experience = generator.create_experience(host=self.user)
        self.amenity1 = generator.create_amenity(name="amenity1", description="desc1")
        self.amenity2 = generator.create_amenity(name="amenity2", description="desc1")
        self.room_review1 = generator.create_review(
            user=self.user,
            room=self.room,
            payload="review_room1",
            rating=3,
        )
        self.room_review1 = generator.create_review(
            user=self.user,
            room=self.room,
            payload="review_room2",
            rating=4,
        )
        self.experience_review1 = generator.create_review(
            user=self.user,
            experience=self.experience,
            payload="review_experience1",
            rating=3,
        )
        self.experience_review2 = generator.create_review(
            user=self.user,
            experience=self.experience,
            payload="review_experience2",
            rating=5,
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

    def test_photos_fields_are_included_room_detail(self):
        target_url = room_detail_url(self.room.id)

        res = self.client.get(target_url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn("photos", res.data.keys())

    def test_post_review_selected_room_raise_error(self):
        target_url = room_review_url(self.room.id)
        payload = {"payload": "hahoho", "rating": 3}
        res = self.client.post(target_url, payload)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRoomApisWithPropertyTest(TestCase):
    def setUp(self):
        self.user = create_user(email="user@example.com", password="password")
        self.room = generator.create_room(owner=self.user)
        self.experience = generator.create_experience(host=self.user)
        self.amenity1 = generator.create_amenity(name="amenity1", description="desc1")
        self.amenity2 = generator.create_amenity(name="amenity2", description="desc1")
        self.room_review1 = generator.create_review(
            user=self.user,
            room=self.room,
            payload="review_room1",
            rating=3,
        )
        self.room_review1 = generator.create_review(
            user=self.user,
            room=self.room,
            payload="review_room2",
            rating=4,
        )
        self.experience_review1 = generator.create_review(
            user=self.user,
            experience=self.experience,
            payload="review_experience1",
            rating=3,
        )
        self.experience_review2 = generator.create_review(
            user=self.user,
            experience=self.experience,
            payload="review_experience2",
            rating=5,
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
        self.client.force_login(self.user)

    def test_post_review_selected_room(self):
        target_url = room_review_url(self.room.id)
        payload = {"payload": "hahoho", "rating": 3}
        res = self.client.post(target_url, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        review = Review.objects.get(id=res.data["id"])
        serializer = ReviewSerializer(review)
        self.assertEqual(serializer.data, res.data)
