from django.urls import path
from rooms import views
from rooms.url_match import (
    get_update_delete_dict,
    get_post_dict,
    get_dict,
)

app_name = "rooms"


urlpatterns = [
    path(
        "",
        views.Rooms.as_view(get_post_dict),
        name="room-list",
    ),
    path(
        "<int:room_id>/",
        views.RoomDetail.as_view(get_update_delete_dict),
        name="room-detail",
    ),
    path(
        "<int:room_id>/reviews/",
        views.RoomReviews.as_view(get_dict),
        name="room-reviews",
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
