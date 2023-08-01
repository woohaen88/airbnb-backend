from django.urls import path

from categories.views import Categories, CategoryDetail

app_name = "category"
urlpatterns = [
    path("", Categories.as_view(), name="list"),
    path("<int:category_id>/", CategoryDetail.as_view(), name="detail"),
]
