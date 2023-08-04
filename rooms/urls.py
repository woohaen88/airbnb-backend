from django.urls import path
from rooms import views
from rooms.url_match import (
    get_update_delete_dict,
    list_create_dict,
    list_dict,
    create_dict,
)

app_name = "rooms"


urlpatterns = [
    path(
        "",
        views.Rooms.as_view(list_create_dict),
        name="room-list",
    ),
    path(
        "<int:room_id>/",
        views.RoomDetail.as_view(get_update_delete_dict),
        name="room-detail",
    ),
    path(
        "<int:room_id>/reviews/",
        views.RoomReviews.as_view(list_create_dict),
        name="room-reviews",
    ),
    path(
        "<int:room_id>/photos/",
        views.RoomPhotos.as_view(create_dict),
        name="room-photos",
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
