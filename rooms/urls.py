from django.urls import path
from rooms import views

app_name = "rooms"

urlpatterns = [
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
