from django.db import IntegrityError
from django.test import TransactionTestCase

from common.utils import DefaultObjectCreate
from rooms.models import Room


class RoomsTest(TransactionTestCase):
    """
    TODO:
    1. categories 속성이 존재하는가? [v]
    2. total_amenities가 반영되는지 확인 [v]
    """

    def __init__(self, setUp: str = ...):
        super().__init__(setUp)
        self.default_object_create = DefaultObjectCreate()

    def setUp(self) -> None:
        self.user = self.default_object_create.create_user()

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

        amenity1 = self.default_object_create.create_amenity(name="item")
        room = Room.objects.create(
            owner=self.user,
            **self.default_object_create.room_defaults,
        )
        room.amenities.add(amenity1)

        self.assertEqual(room.title, str(room))

    def test_create_rooms_with_negative_value(self):
        """price, rooms toilets에 음수를 넣으면 error"""
        for key in ["price", "rooms", "toilets"]:
            copy_param = self.default_object_create.room_defaults.copy()
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

    def test_category_isin_experiences(self):
        room = Room.objects.create(
            owner=self.user,
            **self.default_object_create.room_defaults,
        )

        self.assertTrue(hasattr(room, "category"))

    def test_total_amenity_in_room_model(self):
        """
        room Model에 amenity 2개를 추가하여
        total_amenities 메소드로 체크
        """
        amenity1 = self.default_object_create.create_amenity(name="item1")
        amenity2 = self.default_object_create.create_amenity(name="item2")

        room = self.default_object_create.create_room(owner=self.user)
        room.amenities.add(amenity1, amenity2)

        self.assertEqual(room.total_amenities(), 2)
