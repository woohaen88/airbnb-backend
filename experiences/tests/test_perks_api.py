from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from common.utils import DefaultObjectCreate
from experiences.models import Perk
from experiences.serializers import PerkSerializer

PERKS_URL = reverse("experiences:perks-list")


def perk_detail_url(perk_id: int) -> str:
    return reverse("experiences:perk-detail", kwargs={"perk_id": perk_id})


class PublicPerksApisTest(TestCase):
    def setUp(self) -> None:
        self.default_object_create = DefaultObjectCreate()
        self.client = APIClient()

    # get all Perks
    def test_get_all_perks(self):
        self.default_object_create.create_perk(name="perk1")
        self.default_object_create.create_perk(name="perk2")
        self.default_object_create.create_perk(name="perk3")

        res = self.client.get(PERKS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        perks = Perk.objects.all()
        self.assertEqual(len(perks), 3)
        serializer = PerkSerializer(perks, many=True)
        self.assertEqual(serializer.data, res.data)

    # post Perks
    def test_post_all_perks(self):
        payload = self.default_object_create.perk_defaults.copy()
        res = self.client.post(PERKS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)

        perk = Perk.objects.get(id=res.data["id"])
        for k, v in payload.items():
            self.assertEqual(getattr(perk, k), v)

    # retrieve Perks
    def test_retrieve_perk(self):
        payload = self.default_object_create.perk_defaults.copy()
        perk = Perk.objects.create(**payload)
        url = perk_detail_url(perk.id)

        res = self.client.get(url)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        serializer = PerkSerializer(perk)
        self.assertEqual(res.data, serializer.data)

    # put Perks
    def test_put_perk(self):
        perk = self.default_object_create.create_perk()
        payload = {
            "name": "updated_name",
            "details": "updated_details",
        }

        url = perk_detail_url(perk.id)

        res = self.client.put(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

        perk.refresh_from_db()
        for k, v in payload.items():
            self.assertEqual(getattr(perk, k), v)

    # delete Perks
    def test_delete_perk(self):
        perk = self.default_object_create.create_perk()
        url = perk_detail_url(perk.id)
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
