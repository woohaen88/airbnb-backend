from typing import Any
from django.db import transaction


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


from categories.models import Category
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


class Rooms(APIView):
    def get(self, request: Request):
        rooms = Room.objects.all()
        serializer = RoomListSerializer(rooms, many=True)
        return Response(serializer.data)

    @authentication_required
    def post(self, request: Request, *args, **kwargs):
        serializer: Serializer = RoomDetailSerializer(data=request.data)
        if serializer.is_valid():
            # category validation
            category_id = request.data.get("category")
            if not category_id:
                raise ParseError
            try:
                category = Category.objects.get(id=category_id)
                if category.kind == Category.KindCategoryChoices.EXPERIENCES:
                    raise ParseError("여기는 room 카테고리인데 experiences 카테고리를 입력했구려~")
            except Category.DoesNotExist:
                raise NotFound("해당 카테고리는 존재하지 않음 ㅅㄱ")

            # amenities
            amenities = request.data.get("amenities", None)

            try:
                with transaction.atomic():
                    room = serializer.save(
                        owner=request.user,
                        category=category,
                    )

                    if amenities:
                        for amenity_id in amenities:
                            amenity = Amenity.objects.get(id=amenity_id)
                            room.amenities.add(amenity)
                        serializer = RoomDetailSerializer(room)
                        return Response(serializer.data, status=status.HTTP_201_CREATED)
                    serializer = RoomDetailSerializer(room)
                    return Response(serializer.data, status=status.HTTP_201_CREATED)
            except Exception:
                raise ParseError("Amenity not found")
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RoomDetail(APIView):
    # permission_classes = [IsAuthenticated]

    def get_object(self, room_id: int):
        try:
            return Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise NotFound("해당 Room이 없습니다.")

    def get(self, request: Request, room_id: int):
        room = self.get_object(room_id)
        serializer = RoomDetailSerializer(room)
        return Response(serializer.data)

    @authentication_required
    def put(self, request: Request, room_id: int):
        room = self.get_object(room_id)
        serializer: Serializer = RoomDetailSerializer(
            room,
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            # category
            category_id = request.data.get("category", None)

            if category_id:
                try:
                    category = Category.objects.get(id=category_id)
                    if category.kind != Category.KindCategoryChoices.ROOMS:
                        raise ParseError("여기는 room 카테고리인데 experiences 카테고리를 입력했구려~")

                except Category.DoesNotExist:
                    raise ParseError(f"Category with {category_id} does not exists!!")

            amenities = request.data.get("amenities", None)
            if amenities:
                try:
                    with transaction.atomic():
                        room = serializer.save()
                        for amenity_id in amenities:
                            amenity = Amenity.objects.get(id=amenity_id)
                            room.amenities.add(amenity)
                        serializer = RoomDetailSerializer(room)
                        return Response(serializer.data, status=status.HTTP_200_OK)
                except Exception:
                    raise ParseError("Amenity not found!!!!!!!!!")

            room = serializer.save()
            return Response(RoomDetailSerializer(room).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @authentication_required
    def delete(self, request: Request, room_id: int):
        room = self.get_object(room_id)
        room.delete()
        return Response(status.HTTP_204_NO_CONTENT)
