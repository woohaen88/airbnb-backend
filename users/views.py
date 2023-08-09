from pprint import pprint
import requests
from django.contrib.auth import get_user_model, logout
from django.contrib.auth import login
from rest_framework import mixins
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import ParseError, AuthenticationFailed
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from common.shortcut import get_object_or_404

from users import serializers
from users.serializers import UserSerializer


class CreateJWTView(TokenObtainPairView):
    pass


class VerifyJWTView(TokenVerifyView):
    pass


class RefreshJWTView(TokenRefreshView):
    pass


class CreateUserView(APIView):
    def post(self, request: Request):
        serializer = UserSerializer(
            data=request.data
        )  # email, password, name: optional
        if serializer.is_valid():
            email = request.data.get("email", None)
            password = request.data.get("password", None)
            username = request.data.get("name", None)
            user = get_user_model().objects.create_user(
                email=email,
                password=password,
                username=username,
            )
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {
                "detail": ParseError.default_detail,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class LoginView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = TokenObtainPairSerializer
    queryset = get_user_model().objects.all()

    def create(self, request, *args, **kwargs):
        # email과 password는 None값이 아님
        email = request.data.get("email", None)
        password = request.data.get("password", None)

        assert (email is not None) or (
            password is not None
        ), " email or password값이 없습니다."

        user = get_object_or_404(get_user_model(), email=email)
        if not user.check_password(password):
            raise AuthenticationFailed
        login(request, user)

        response = Response(
            {
                "user": serializers.TinyUserSerializer(user).data,
                "message": "login success",
            },
            status=status.HTTP_200_OK,
        )

        return response


class LogoutView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.UserLogoutSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logout(request)
        response = Response(
            {"message": "Logout success"}, status=status.HTTP_202_ACCEPTED
        )
        return response


class UserMeView(
    mixins.ListModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.PrivateUserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user

    def list(self, request, *args, **kwargs):
        user = self.get_queryset()
        serializer = self.get_serializer(user)
        return Response(serializer.data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        user = self.get_queryset()
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        update_user = self.perform_update(serializer)
        update_serializer = self.get_serializer(update_user)
        return Response(update_serializer.data)

    def perform_update(self, serializer, **kwargs):
        return serializer.save(**kwargs)


class UserChangePasswordView(
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    queryset = get_user_model().objects.all()
    serializer_class = serializers.PasswordChangeSerializer

    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", True)
        user = self.get_queryset()
        raw_password = request.data.get("raw_password")
        change_password = request.data.get("change_password")

        assert (raw_password or change_password) is not None, "저기여! 입력값을 제대로 주셔야죠~"
        serializer = self.get_serializer(user, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        return Response({"details: 패스워드를 바꾸셨군여!"}, status=status.HTTP_200_OK)

    def perform_update(self, serializer):
        return serializer.save()


class GithubLogIn(
    mixins.CreateModelMixin,
    viewsets.GenericViewSet,
):
    serializer_class = serializers.SocialLocalSerializer
    queryset = get_user_model().objects.all()

    def create(self, request, *args, **kwargs):
        try:
            return self.perform_create(request, *args, **kwargs)
        except Exception:
            raise ParseError("로그인 인증 실패 했어여!!")

    def perform_create(self, request, *args, **kwargs):
        code = request.data.get("code")
        client_id = "3134f37421010b5af5fe"
        client_secret = "8110fb973f681ad87c0cf8b21f658fb5c931adfb"
        token = requests.post(
            f"https://github.com/login/oauth/access_token?code={code}&client_id={client_id}&client_secret={client_secret}",
            headers={"Accept": "application/json"},
        )

        token = token.json()
        access_token = token.get("access_token")
        user_data = requests.get(
            "https://api.github.com/user",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        user_data = user_data.json()

        emails_data = requests.get(
            "https://api.github.com/user/emails",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        emails_data = emails_data.json()

        avatar_url = user_data.get("avatar_url")
        username = user_data.get("login")
        email = emails_data[0]["email"]

        try:
            user = get_user_model().objects.get(email=email)
            login(request, user)

            response = Response(status=status.HTTP_200_OK)

            return response
        except Exception:
            user = get_user_model().objects.create(
                email=email, username=username, avatar=avatar_url
            )
            user.set_unusable_password()
            user.save()
            login(request, user)

            response = Response(status=status.HTTP_200_OK)

            return response
