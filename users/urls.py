from django.urls import path

from common import url_match
from users import views

app_name = "users"
urlpatterns = [
    path(
        "create/",
        views.CreateUserView.as_view(),
        name="create",
    ),
    path(
        "login/",
        views.LoginView.as_view(url_match.create_dict),
        name="login",
    ),
    path(
        "logout/",
        views.LogoutView.as_view(url_match.create_dict),
        name="logout",
    ),
    path(
        "token/",
        views.CreateJWTView.as_view(),
        name="token-create",
    ),  # jwt 인증 url
    path(
        "token/verify/",
        views.VerifyJWTView.as_view(),
        name="token-verify",
    ),  # jwt 인증 url
    path(
        "token/refresh/",
        views.RefreshJWTView.as_view(),
        name="token-refresh",
    ),  # jwt refresh url
    path(
        "me/",
        views.UserMeView.as_view(url_match.list_update_dict),
        name="me",
    ),
    path(
        "change-password/",
        views.UserChangePasswordView.as_view(url_match.update_dict),
        name="change-password",
    ),
]
