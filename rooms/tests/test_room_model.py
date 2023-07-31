from django.db import IntegrityError
from django.test import TransactionTestCase
from rooms.models import Room, Amenity
from django.contrib.auth import get_user_model


class RoomsTest(TransactionTestCase):
    def setUp(self) -> None:
        self.user = get_user_model().objects.create_user(
            "test@example.com", "test123!@#"
        )

        self.defaults = dict(
            title="title",
            country="한국",
            city="서울",
            price=123012,
            rooms=2,
            toilets=3,
            description="description",
            address="address",
            pet_friendly=True,
            kind="entire_place",
        )

    def test_create_rooms_with_correct_data(self):
        """
        create Room models and return title

        FK: User
        MtoM: Amenity

        price: 가격, 양의 정수만 가능
        rooms: 방의 갯수, 양의 정수만 가능
        toilets = 방의 갯수, 양의 정수만 가능
        descriptions:
        address:
        pet_friendly: boolean
        kind: Enum(entire_place, private_room, shared_room ONLY)
        """

        amenity1 = Amenity.objects.create(name="item1", description="hahohaho")
        updated_param = self.defaults.copy()
        room = Room.objects.create(
            owner=self.user,
            **updated_param,
        )
        room.amenities.add(amenity1)

        self.assertEqual(room.title, str(room))

    def test_create_rooms_with_negative_value(self):
        """price, rooms toilets에 음수를 넣으면 error"""
        for key in ["price", "rooms", "toilets"]:
            copy_param = self.defaults.copy()
            copy_param.update({key: -1})

            with self.assertRaises(IntegrityError):
                room = Room.objects.create(
                    owner=self.user,
                    **copy_param,
                )

    # save() 수준에서 제어
    # def test_create_rooms_with_negative_value(self):
    #     """
    #     kind: Enum(entire_place, private_room, shared_room ONLY)
    #     외에 다른 값이 들어가면 error
    #     :return:
    #     """
    #     copy_param = self.defaults.copy()
    #     copy_param.update({"kind": "hahaho"})
    #
    #     with self.assertRaises(IntegrityError):
    #         room = Room.objects.create(
    #             owner=self.user,
    #             **copy_param,
    #         )
