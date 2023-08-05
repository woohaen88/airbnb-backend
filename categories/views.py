from typing import Any

from django.db.models import QuerySet
from rest_framework import status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.serializers import Serializer
from rest_framework.views import APIView

from categories.models import Category
from categories.serializers import CategorySerializer


class Categories(APIView):
    def get(self, request: Request) -> Response:
        all_categories: QuerySet[Category] = Category.objects.all()
        serializer: Serializer = CategorySerializer(all_categories, many=True)

        return Response(serializer.data)

    def post(self, request: Request) -> Response:
        serializer: Serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            new_category: Any = serializer.save()
            return Response(
                CategorySerializer(new_category).data,
            )
        else:
            return Response(serializer.errors)


class CategoryDetail(APIView):
    def get_object(self, id: int) -> Any:
        try:
            return Category.objects.get(id=id)
        except Category.DoesNotExist:
            raise NotFound

    def get(self, request: Request, category_id: int) -> Response:
        serializer: Serializer = CategorySerializer(self.get_object(id=category_id))
        return Response(serializer.data)

    def put(self, request: Request, category_id: int) -> Response:
        serializer: Serializer = CategorySerializer(
            self.get_object(id=category_id),
            data=request.data,
            partial=True,
        )
        if serializer.is_valid():
            updated_category: Any = serializer.save()
            return Response(CategorySerializer(updated_category).data)
        return Response(serializer.errors)

    def delete(self, request: Request, category_id: int) -> Response:
        self.get_object(id=category_id).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
