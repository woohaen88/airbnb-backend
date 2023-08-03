from functools import wraps
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated, PermissionDenied
from rest_framework import status


def authentication_required(func):
    # decorated함수의 arguments (self 포함)하여 모두 인자로 받음
    @wraps(func)
    def wrapper(apiview_class, request: Request, *args, **kwargs):
        # authentication
        if not request.user.is_authenticated:
            return Response(
                NotAuthenticated.default_detail,
                status=status.HTTP_401_UNAUTHORIZED,
            )

        # authenticated_user와 owner가 같은지 check
        try:
            instance = apiview_class.get_object(*args, **kwargs)  # room
            for fk in ["owner", "host"]:
                if hasattr(instance, fk):
                    if getattr(instance, fk) != request.user:
                        return Response(
                            PermissionDenied.default_detail,
                            status=status.HTTP_403_FORBIDDEN,
                        )
        except Exception:
            pass

        return func(apiview_class, request, *args, **kwargs)

    return wrapper
