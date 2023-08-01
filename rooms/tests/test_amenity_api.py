from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from common.utils import DefaultObjectCreate
from rooms.models import Amenity
from rooms.serializers import AmenitySerializer

AMENITY_URL = reverse("rooms:amenity-list")


def amenity_detail_url(amenity_id: int) -> str:
    return reverse(
        "rooms:amenity-detail",
        kwargs={
            "amenity_id": amenity_id,
        },
    )


class PublicAmenityAPITests(TestCase):
    def setUp(self) -> None:
        self.default_object_create = DefaultObjectCreate()
        self.client = APIClient()

    def test_get_all_amenities(self):
        self.default_object_create.create_amenity(name="item1")
        self.default_object_create.create_amenity(name="item2")

        res = self.client.get(AMENITY_URL)
        amenities = Amenity.objects.all()
        serializer = AmenitySerializer(amenities, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_amenity(self):
        """post"""
        payload = {
            "name": "test_name",
            "description": "test_description",
        }
        res = self.client.post(AMENITY_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        amenity = Amenity.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(amenity, k), v)

    def test_get_amenity_detail(self):
        """Test get amenity detail"""
        amenity = self.default_object_create.create_amenity(name="item1")
        url = amenity_detail_url(amenity.id)
        res = self.client.get(url)

        serializer = AmenitySerializer(amenity)
        self.assertEqual(serializer.data, res.data)

    def test_partial_update(self):
        """Test partial update of amenity"""
        amenity = self.default_object_create.create_amenity(name="item1")
        updated_name = "update_item1"

        payload = {
            "name": updated_name,
        }

        url = amenity_detail_url(amenity.id)
        res = self.client.put(url, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        amenity.refresh_from_db()
        self.assertEqual(amenity.name, payload["name"])

    def test_delete_amenity(self):
        """Test deleting a amenity"""
        amenity = self.default_object_create.create_amenity(name="item1")
        url = amenity_detail_url(amenity.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Amenity.objects.filter(id=amenity.id).exists())
