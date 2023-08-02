from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import NotAuthenticated, ParseError, AuthenticationFailed
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.authtoken.views import ObtainAuthToken


from users.serializers import UserSerializer, AuthTokenSerializer


class CreateUserView(APIView):
    def post(self, request: Request):
        serializer = UserSerializer(
            data=request.data
        )  # email, password, name: optional
        if serializer.is_valid():
            email = request.data.get("email", None)
            password = request.data.get("password", None)
            name = request.data.get("name", None)
            user = get_user_model().objects.create_user(
                email=email,
                password=password,
                name=name,
            )
            serializer = UserSerializer(user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            {
                "detail": ParseError.default_detail,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )


class CreateTokenView(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = AuthTokenSerializer(
            data=request.data,
            context={"request": request},
        )

        if serializer.is_valid():
            user = serializer.validated_data["user"]
            token, created = Token.objects.get_or_create(user=user)
            return Response(
                {
                    "token": token.key,
                    "email": user.email,
                },
                status=status.HTTP_201_CREATED,
            )

        return Response(
            {
                "detail": ParseError.default_detail,
            },
            status=status.HTTP_400_BAD_REQUEST,
        )
