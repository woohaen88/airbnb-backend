from django.urls import path
from wishlists import views
from common.url_match import list_create_dict, retrieve_update_destroy_dict

app_name = "wishlists"
urlpatterns = [
    path("", views.WishlistsView.as_view(list_create_dict), name="list"),
    path(
        "<int:wishlist_id>",
        views.WishlistDetailView.as_view(retrieve_update_destroy_dict),
        name="detail",
    ),
]
