from typing import Any

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404

from rest_framework import status
from rest_framework.exceptions import (
    NotFound,
    NotAuthenticated,
    ParseError,
    PermissionDenied,
)
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    RetrieveModelMixin,
    DestroyModelMixin,
    UpdateModelMixin,
)


from categories.models import Category
from common.exceptions import get_object_or_400
from medias.models import Photo
from medias.serializers import PhotoSerializer
from reviews.serializers import ReviewSerializer
from rooms.models import Amenity, Room
from rooms.serializers import (
    AmenitySerializer,
    RoomDetailSerializer,
    RoomListSerializer,
)
from config.permissions.decorators import authentication_required


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
    # permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == "list":
            return RoomListSerializer
        return self.serializer_class

    def list(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.queryset, many=True)
        return Response(serializer.data)

    @authentication_required
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
    lookup_field = "id"
    lookup_url_kwarg = "room_id"
    queryset = Room.objects.all()
    serializer_class = RoomDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @authentication_required
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        instance = self.get_object()
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

    @authentication_required
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        instance.delete()


class RoomReviews(ListModelMixin, GenericViewSet):
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


class RoomPhotos(CreateModelMixin, GenericViewSet):
    queryset = Room.objects.all()
    serializer_class = PhotoSerializer
    lookup_field = "id"
    lookup_url_kwarg = "room_id"

    @authentication_required
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
