from django.urls import path
from medias import views
from medias.url_match import destroy_dict

app_name = "medias"
urlpatterns = [
    path(
        "photos/<int:photo_id>/",
        views.PhotoDetailView.as_view(destroy_dict),
        name="photo-delete",
    ),
]
