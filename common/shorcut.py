from rest_framework.exceptions import NotFound


def get_object_or_404(model, *args, **kwargs):
    try:
        return model.objects.get(*args, **kwargs)
    except model.DoesNotExist:
        raise NotFound(f"저기요!! {kwargs}을 가진 {model.__name__} 객체는 없어욧!!")
