from django.urls import path

from experiences import views

app_name = "experiences"
urlpatterns = [
    path("perks/", views.Perks.as_view(), name="perks-list"),
    path("perks/<int:perk_id>/", views.PerkDetail.as_view(), name="perk-detail"),
]
