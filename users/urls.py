from django.urls import path
from users import views
from common.url_match import create_dict, retrieve_dict

app_name = "users"
urlpatterns = [
    path(
        "create/",
        views.CreateUserView.as_view(),
        name="create",
    ),
    path(
        "login/",
        views.LoginView.as_view(create_dict),
        name="login",
    ),
    path(
        "logout/",
        views.LogoutView.as_view(create_dict),
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
        views.UserMeView.as_view(retrieve_dict),
        name="me",
    ),
]
