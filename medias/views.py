from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.mixins import DestroyModelMixin
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from rest_framework.permissions import IsAuthenticated

from medias.models import Photo
from medias.serializers import PhotoSerializer

from config.authentication import SimpleJWTAuthentication


class PhotoDetailView(DestroyModelMixin, GenericViewSet):
    queryset = Photo.objects.all()
    serializer_class = PhotoSerializer
    lookup_field = "id"
    lookup_url_kwarg = "photo_id"
    authentication_classes = [SimpleJWTAuthentication]
    permission_classes = [IsAuthenticated]

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
