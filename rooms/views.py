from typing import Any

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from rooms.models import Amenity
from rooms.serializers import AmenitySerializer


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

    def get_object(self, amenity_id: int) -> Any:
        try:
            return Amenity.objects.get(id=amenity_id)
        except Amenity.DoesNotExist:
            raise NotFound("해당 Amenity를 찾을 수 없습니다.")

    def get(self, request: Request, amenity_id) -> Response:
        amenity = self.get_object(amenity_id=amenity_id)
        serializer = AmenitySerializer(amenity)
        return Response(serializer.data)

    def put(self, request: Request, amenity_id) -> Response:
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

    def delete(self, request: Request, amenity_id) -> Response:
        amenity = self.get_object(amenity_id=amenity_id)
        amenity.delete()
        return Response(
            {
                "message": "amenity Delete",
            },
            status=status.HTTP_204_NO_CONTENT,
        )
