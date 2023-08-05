from rest_framework.exceptions import (
    NotFound,
    AuthenticationFailed,
    ParseError,
)


def get_object_or_404(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        raise NotFound(f"저기요!! {kwargs}을 가진 {model.__name__} 객체는 없어욧!!")


def get_object_or_400(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        raise ParseError(f"저기요!! {kwargs}을 가진 {model.__name__} 객체는 없어욧!!")


def get_object_or_401(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        raise AuthenticationFailed(f"저기요!! {kwargs}을 가진 {model.__name__} 객체는 없어욧!!")
