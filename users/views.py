from django.contrib.auth import login, logout
from rest_framework import mixins
from rest_framework import viewsets
from django.contrib.auth import get_user_model
from rest_framework import status

from rest_framework.exceptions import NotAuthenticated, ParseError, AuthenticationFailed
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from users import serializers


from users.serializers import TinyUserSerializer, UserSerializer
from common.shortcut import get_object_or_404


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


from rest_framework.permissions import IsAuthenticated

from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from config.authentication import SimpleJWTAuthentication


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

        token = self.get_serializer_class().get_token(user)
        refresh_token = str(token)  # refresh 토큰 문자열화
        access_token = str(token.access_token)  # access 토큰 문자열화
        response = Response(
            {
                "user": serializers.TinyUserSerializer(user).data,
                "message": "login success",
                "jwt_token": {
                    "access_token": access_token,
                    "refresh_token": refresh_token,
                },
            },
            status=status.HTTP_200_OK,
        )
        response.set_cookie(
            "access_token",
            access_token,
            httponly=True,
            secure=False,
        )
        response.set_cookie(
            "refresh_token",
            refresh_token,
            httponly=True,
            secure=False,
        )
        return response


class LogoutView(mixins.CreateModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.UserLogoutSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def create(self, request, *args, **kwargs):
        logout(request)
        return Response(
            {"details": "logout!!"},
            status=status.HTTP_200_OK,
        )


class UserMeView(mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    serializer_class = TinyUserSerializer
    queryset = get_user_model().objects.all()
    permission_classes = [IsAuthenticated]
    authentication_classes = [SimpleJWTAuthentication]

    def get_object(self):
        return self.request.user

    def get_queryset(self):
        return get_user_model().objects.get(id=self.request.user.id)

    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user)
        return Response(serializer.data)
