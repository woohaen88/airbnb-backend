from django.test import TestCase
from rooms.models import Amenity


class AmenityModelTest(TestCase):
    def test_create_amenity_model(self):
        name = "item1"
        amenity1 = Amenity.objects.create(name=name)
        self.assertEqual(amenity1.name, str(amenity1))

        # verbose_name_plural
        self.assertEqual("amenities", amenity1._meta.verbose_name_plural)
