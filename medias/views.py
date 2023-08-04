from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import DestroyModelMixin

from medias.models import Photo
from medias.serializers import RoomPhotoSerializer
from config.permissions.decorators import authentication_required


class PhotoDetailView(DestroyModelMixin, GenericViewSet):
    queryset = Photo.objects.all()
    serializer_class = RoomPhotoSerializer
    lookup_field = "id"
    lookup_url_kwarg = "photo_id"

    @authentication_required
    def destroy(self, request, *args, **kwargs):
        photo = self.get_object()
        self.perform_destroy(photo)
        return Response(status=status.HTTP_204_NO_CONTENT)

    def perform_destroy(self, instance):
        if (instance.room and instance.room.owner != self.request.user) or (
            instance.experiences and instance.experience.host != self.request.user
        ):
            raise PermissionDenied
        instance.delete()
