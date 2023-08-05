from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import (
    NotFound,
    ParseError,
    PermissionDenied,
)
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
)
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from bookings.models import Booking
from bookings.serializers import PublicBookingSerializer, CreateRoomBookingSerializer
from categories.models import Category
from common.exceptions import get_object_or_400
from config.authentication import SimpleJWTAuthentication
from medias.serializers import PhotoSerializer
from reviews.serializers import ReviewSerializer
from rooms.models import Amenity, Room
from rooms.serializers import (
    AmenitySerializer,
    RoomDetailSerializer,
    RoomListSerializer,
)


class Amenities(APIView):
    """/api/v1/rooms/amenities"""

    def get(self, request):
        all_amenities = Amenity.objects.all()
        serializer = AmenitySerializer(all_amenities, many=True)
        return Response(serializer.data)

    def post(self, request: Request):
        serializer = AmenitySerializer(data=request.data)
        if serializer.is_valid():
            amenity = serializer.save()
            return Response(AmenitySerializer(amenity).data)

        return Response(serializer.errors)


class AmenityDetail(APIView):
    """/api/v1/rooms/amenities/1"""

    def get_object(self, amenity_id: int):
        try:
            return Amenity.objects.get(id=amenity_id)
        except Amenity.DoesNotExist:
            raise NotFound("해당 Amenity를 찾을 수 없습니다.")

    def get(self, request: Request, amenity_id):
        amenity = self.get_object(amenity_id=amenity_id)
        serializer = AmenitySerializer(amenity)
        return Response(serializer.data)

    def put(self, request: Request, amenity_id):
        amenity = self.get_object(amenity_id=amenity_id)
        serializer = AmenitySerializer(
            amenity,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            amenity = serializer.save()
            return Response(AmenitySerializer(amenity).data)
        return Response(serializer.errors)

    def delete(self, request: Request, amenity_id):
        amenity = self.get_object(amenity_id=amenity_id)
        amenity.delete()
        return Response(
            {
                "message": "amenity Delete",
            },
            status=status.HTTP_204_NO_CONTENT,
        )


class Rooms(
    ListModelMixin,
    CreateModelMixin,
    GenericViewSet,
):
    queryset = Room.objects.all()

    serializer_class = RoomDetailSerializer
    authentication_classes = [SimpleJWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return RoomListSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        room = self.perform_create(serializer)
        serializer = self.get_serializer(room)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer):
        category_id = self.request.data.get("category", None)
        if not category_id:
            raise ParseError("Category 없어욧 후후후")

        category = get_object_or_404(Category, id=category_id)
        if category.kind == Category.KindCategoryChoices.EXPERIENCES:
            raise ParseError("ROOM 카테고리만 넣을 수 있어요")

        amenities = self.request.data.get("amenities", [])
        try:
            with transaction.atomic():
                room = serializer.save(
                    owner=self.request.user,
                    category=category,
                )
                for amenity_id in amenities:
                    amenity = Amenity.objects.get(id=amenity_id)
                    room.amenities.add(amenity)
                return room
        except Exception:
            raise ParseError("Amenity not found")


class RoomDetail(
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [SimpleJWTAuthentication]
    lookup_field = "id"
    lookup_url_kwarg = "room_id"
    queryset = Room.objects.all()
    serializer_class = RoomDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
        if instance.owner != request.user:
            raise PermissionDenied("니가 작성한 것도 아닌데 수정하면 오또케~~")
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        room = self.perform_update(serializer)
        updated_serializer = self.get_serializer(room)
        return Response(updated_serializer.data)

    def perform_update(self, serializer):
        category_id = self.request.data.get("category", None)
        if category_id:
            category = get_object_or_400(Category, id=category_id)
            if category.kind != Category.KindCategoryChoices.ROOMS:
                raise ParseError("저기요!! 룸 카테고리만 넣을 수 있어요!")

        amenities = self.request.data.get("amenities", None)
        if amenities:
            try:
                with transaction.atomic():
                    room = serializer.save()
                    for amenity_id in amenities:
                        amenity = Amenity.objects.get(id=amenity_id)
                        room.amenities.add(amenity)
                    return room
            except Exception:
                raise ParseError("Amenity not found")

        room = serializer.save()
        return room

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class RoomReviews(
    ListModelMixin,
    CreateModelMixin,
    GenericViewSet,
):
    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [SimpleJWTAuthentication]
    queryset = Room.objects.all()
    serializer_class = ReviewSerializer
    lookup_field = "id"
    lookup_url_kwarg = "room_id"

    def list(self, request, *args, **kwargs):
        try:
            page = request.query_params.get("page", 1)
            page = int(page)
        except ValueError:
            page = 1
        page_size = settings.PAGE_SIZE

        start = page_size * (page - 1)
        end = start + 3
        room = self.get_object()
        serializer = self.get_serializer(room.reviews.all()[start:end], many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        room = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        review = self.perform_create(serializer, user=request.user, room=room)
        updated_serializer = self.get_serializer(review)
        headers = self.get_success_headers(updated_serializer.data)
        return Response(
            updated_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer, **kwargs):
        return serializer.save(**kwargs)


class RoomPhotos(CreateModelMixin, GenericViewSet):
    permission_classes = [IsAuthenticated]
    authentication_classes = [SimpleJWTAuthentication]
    queryset = Room.objects.all()
    serializer_class = PhotoSerializer
    lookup_field = "id"
    lookup_url_kwarg = "room_id"

    def create(self, request, *args, **kwargs):
        room = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        photo = self.perform_create(serializer, room=room)
        updated_serializer = self.get_serializer(photo)
        headers = self.get_success_headers(serializer.data)
        return Response(
            updated_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer, **kwargs):
        return serializer.save(**kwargs)


class RoomBookingView(
    CreateModelMixin,
    ListModelMixin,
    GenericViewSet,
):
    queryset = Room.objects.all()
    serializer_class = PublicBookingSerializer
    lookup_field = "id"
    lookup_url_kwarg = "room_id"

    permission_classes = [IsAuthenticatedOrReadOnly]
    authentication_classes = [SimpleJWTAuthentication]

    def get_serializer_class(self):
        if self.action == "create":
            return CreateRoomBookingSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        room = self.get_object()  # room_id로 쿼리 조회
        now = timezone.localtime(timezone.now()).date()
        bookings = Booking.objects.filter(
            room=room,
            kind=Booking.BookingKindChoices.ROOM,
            check_in__gt=now,
        )
        serializer = self.get_serializer(bookings, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        room = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        updated_room = self.perform_create(
            serializer,
            room=room,
            user=request.user,
            kind=Booking.BookingKindChoices.ROOM,
        )
        updated_serializer = self.get_serializer(updated_room)
        headers = self.get_success_headers(updated_serializer.data)
        return Response(
            updated_serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def perform_create(self, serializer, **kwargs):
        return serializer.save(**kwargs)
