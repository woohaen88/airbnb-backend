from django.urls import path
from rooms import views
from rooms.url_match import get_update_delete, get_post_dict

app_name = "rooms"


urlpatterns = [
    path(
        "",
        views.Rooms.as_view(get_post_dict),
        name="room-list",
    ),
    path(
        "<int:room_id>/",
        views.RoomDetail.as_view(get_update_delete),
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
