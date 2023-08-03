from django.urls import path
from rooms import views

app_name = "rooms"


urlpatterns = [
    path(
        "",
        views.Rooms.as_view(
            {
                "get": "list",
                "post": "create",
            }
        ),
        name="room-list",
    ),
    path(
        "<int:room_id>/",
        views.RoomDetail.as_view(),
        name="room-detail",
    ),
    path(
        "amenities/",
        views.Amenities.as_view(),
        name="amenity-list",
    ),
    path(
        "amenities/<int:amenity_id>/",
        views.AmenityDetail.as_view(),
        name="amenity-detail",
    ),
]
