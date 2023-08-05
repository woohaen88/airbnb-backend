from django.utils import timezone
from rest_framework import serializers

from bookings.models import Booking


class PublicBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            "id",
            "check_in",
            "check_out",
            "experience_time",
            "guests",
        )


class PrivateBookingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = (
            "id",
            "check_in",
            "check_out",
            "experience_time",
            "guests",
        )


class CreateRoomBookingSerializer(serializers.ModelSerializer):
    check_in = serializers.DateField()
    check_out = serializers.DateField()

    class Meta:
        model = Booking
        fields = (
            "check_in",
            "check_out",
            "guests",
        )

    def validate_check_in(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise serializers.ValidationError("저기요! 과거날짜에는 예약이 안되자나여!")
        return value

    def validate_check_out(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise serializers.ValidationError("저기요! 과거날짜에는 예약이 안되자나여!")
        return value

    def validate(self, attr):
        if attr["check_out"] <= attr["check_in"]:
            raise serializers.ValidationError("저기여!! 체크아웃이 체크인보다 빠르면 오또케~")

        exist = Booking.objects.filter(
            check_in__lte=attr["check_out"],
            check_out__gte=attr["check_in"],
        ).exists()
        if exist:
            raise serializers.ValidationError("이미 예약된 방을 예약하려하면 오또케")
        return attr
