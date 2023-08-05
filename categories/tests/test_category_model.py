from django.test import TestCase

from categories.models import Category


class CategoryTest(TestCase):
    def setUp(self) -> None:
        self.category_defaults = {
            "name": "category",  # 50
            "kind": "rooms",  # rooms, experiences, 15
        }

    def test_create_category_model(self):
        category_defaults = self.category_defaults.copy()
        category = Category.objects.create(**category_defaults)

        self.assertEqual(f"{category.kind}: {category.name}", str(category))
        self.assertEqual(category._meta.verbose_name_plural, "categories")
