from rest_framework import status

from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
)

from common.shorcut import get_object_or_404
from rooms.models import Room
from wishlists.models import Wishlist
from wishlists.serializers import WishlistSerializer, WishlistToggleSerializer
from config.permissions.decorators import authentication_required


class WishlistsView(
    ListModelMixin,
    CreateModelMixin,
    GenericViewSet,
):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @authentication_required
    def list(self, request, *args, **kwargs):
        wishlists = self.filter_queryset(self.get_queryset())
        print(wishlists)
        serializer = self.get_serializer(wishlists, many=True)
        return Response(serializer.data)

    @authentication_required
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        wishlist = self.perform_create(serializer, user=request.user)

        updated_serializer = self.get_serializer(wishlist)

        headers = self.get_success_headers(updated_serializer.data)
        return Response(
            updated_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer, **kwargs):
        return serializer.save(**kwargs)


class WishlistDetailView(
    RetrieveModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    GenericViewSet,
):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    lookup_field = "id"
    lookup_url_kwarg = "wishlist_id"

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @authentication_required
    def retrieve(self, request, *args, **kwargs):
        wishlist = self.get_object()
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)

    @authentication_required
    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        wishlist = self.get_object()
        serializer = self.get_serializer(wishlist, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)

        updated_wishlist = self.perform_update(serializer)
        updated_serializer = self.get_serializer(updated_wishlist)
        return Response(updated_serializer.data)

    def perform_update(self, serializer, **kwargs):
        return serializer.save(**kwargs)

    @authentication_required
    def destroy(self, request, *args, **kwargs):
        wishlist = self.get_object()
        self.perform_destroy(wishlist)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, wishlist):
        wishlist.delete()


class WishlistToggleView(UpdateModelMixin, GenericViewSet):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistToggleSerializer
    lookup_field = "id"
    lookup_url_kwarg = "wishlist_id"

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    @authentication_required
    def update(self, request, *args, **kwargs):
        wishlist = self.get_object()
        room = get_object_or_404(Room, id=kwargs.get("room_id"))

        rooms = wishlist.rooms
        rooms.remove(room) if rooms.filter(id=room.id).exists() else rooms.add(room)

        return Response(status=status.HTTP_200_OK)
