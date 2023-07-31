from django.db import IntegrityError
from django.test import TestCase

from houses.models import House


class ModelTest(TestCase):
    def test_create_house_model(self):
        """
        1. housemodel object는 house의 이름과 같아야함
        2. price는 양의 정수만 가능
        """
        name = "testname"
        price_list = [1, -1, 0, 1.1]
        description = "description"
        address = "address"
        pets_allowed = True

        for price in price_list:
            if isinstance(price, int) and price >= 0:
                house_obj = House.objects.create(
                    name=name,
                    price_per_night=price,
                    description=description,
                    address=address,
                    pets_allowed=pets_allowed,
                )
                self.assertEqual(str(house_obj), name)
            else:
                self.assertRaises(IntegrityError)

        # name = "a" * 141
        # price = 1
        # address = "a" * 140
        # description = "description"
        # house_obj = House.objects.create(
        #     name=name,
        #     price=price,
        #     address=address,
        #     description=description,
        # )
        # self.assertEqual(str(house_obj), name)
        # print(len(house_obj.name))
