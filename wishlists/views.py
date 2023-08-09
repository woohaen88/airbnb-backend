from rest_framework import status
from rest_framework.mixins import (
    ListModelMixin,
    CreateModelMixin,
    UpdateModelMixin,
    DestroyModelMixin,
    RetrieveModelMixin,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from common.shortcut import get_object_or_404
from config.authentication import SimpleJWTAuthentication
from rooms.models import Room
from wishlists.models import Wishlist
from wishlists.serializers import WishlistSerializer, WishlistToggleSerializer


class WishlistsView(
    ListModelMixin,
    CreateModelMixin,
    GenericViewSet,
):
    queryset = Wishlist.objects.all()
    serializer_class = WishlistSerializer
    permission_classes = [IsAuthenticated]
    authentication_classes = [SimpleJWTAuthentication]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def list(self, request, *args, **kwargs):
        wishlists = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(
            wishlists, many=True, context={"request": request}
        )
        return Response(serializer.data)

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        wishlist = self.get_object()
        serializer = self.get_serializer(wishlist)
        return Response(serializer.data)

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def update(self, request, *args, **kwargs):
        wishlist = self.get_object()
        room = get_object_or_404(Room, id=kwargs.get("room_id"))

        rooms = wishlist.rooms
        rooms.remove(room) if rooms.filter(id=room.id).exists() else rooms.add(room)

        return Response(status=status.HTTP_200_OK)
