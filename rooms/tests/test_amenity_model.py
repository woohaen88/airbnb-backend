from django.test import TestCase
from rooms.models import Amenity


class AmenityModelTest(TestCase):
    def test_create_amenity_model(self):
        name = "item1"
        amenity1 = Amenity.objects.create(name=name)
        self.assertEqual(amenity1.name, str(amenity1))
