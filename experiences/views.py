from typing import Any

from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from experiences.models import Perk
from experiences.serializers import PerkSerializer


class Perks(APIView):
    def get(self, request: Request) -> Response:
        perks = Perk.objects.all()
        serializer = PerkSerializer(perks, many=True)
        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer = PerkSerializer(data=request.data)
        if serializer.is_valid():
            perk = serializer.save()
            return Response(PerkSerializer(perk).data)
        return Response(serializer.errors)


class PerkDetail(APIView):
    def get_object(self, perk_id: int) -> Any:
        try:
            return Perk.objects.get(id=perk_id)
        except Perk.DoesNotExist:
            raise NotFound("해당 Perk가 존재하지 않습니다.")

    def get(self, request: Request, perk_id: int) -> Response:
        perk = self.get_object(perk_id=perk_id)
        serializer = PerkSerializer(perk)
        return Response(serializer.data)

    def put(self, request: Request, perk_id: int) -> Response:
        perk = self.get_object(perk_id)
        serializer = PerkSerializer(perk, data=request.data)
        if serializer.is_valid():
            perk = serializer.save()
            return Response(PerkSerializer(perk).data)
        return Response(serializer.errors)

    def delete(self, request: Request, perk_id: int) -> Response:
        perk = self.get_object(perk_id)
        return Response(
            data={"message": "perk delete!!"},
            status=status.HTTP_204_NO_CONTENT,
        )
