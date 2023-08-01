from django.test import TestCase

from bookings.models import Booking
from common.utils import DefaultObjectCreate
from django.utils import timezone
from django.db import IntegrityError


class BookingsModelTest(TestCase):
    """
    TODO:
    1. Bookingobject가 "kind",
                    "user",
                    "room",
                    "experience",
                    "check_in",
                    "check_out",
                    "experience_time",
                    "guests",
                    "updated_at",
                    "created_at",
                    속성을 가지고 있어야 함[v]
    2. check_in < check_out [] - api 에서 처리
    3. guests에 음수가 들어오면 error [v]
    4.Bookingobject가 f"{.kind.title()} booking for: {.user}"를 리턴 []
    """

    def setUp(self) -> None:
        defaultObjectCreate = DefaultObjectCreate()
        self.user = defaultObjectCreate.create_user()
        self.experience = defaultObjectCreate.create_experience(host=self.user)
        self.room = defaultObjectCreate.create_room(owner=self.user)

    def test_property_booking_object(self):
        """
        1. 속성을 가지고 있어야함
        2. Bookingobject가 f"{.kind.title()} booking for: {.user}"를 리턴
        """
        extra_fields = dict(
            check_in="2023-07-28",
            check_out="2023-07-28",
            experience_time=timezone.now(),
            guests=3,
        )
        booking = Booking.objects.create(
            user=self.user, experience=self.experience, room=self.room, **extra_fields
        )

        check_list = [
            "kind",
            "user",
            "room",
            "experience",
            "check_in",
            "check_out",
            "experience_time",
            "guests",
            "updated_at",
            "created_at",
        ]
        for check in check_list:
            self.assertTrue(hasattr(booking, check))

        self.assertEqual(
            f"{booking.kind.title()} booking for: {booking.user}", str(booking)
        )

    def test_guests_have_negative_number_return_error(self):
        """
        3. guests에 음수가 들어오면 error [v]
        """
        extra_fields = dict(
            check_in="2023-07-28",
            check_out="2023-07-28",
            experience_time=timezone.now(),
            guests=-1,
        )

        with self.assertRaises(IntegrityError):
            booking = Booking.objects.create(
                user=self.user,
                experience=self.experience,
                room=self.room,
                **extra_fields,
            )
