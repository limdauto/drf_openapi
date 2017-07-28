from functools import wraps

from typing import Callable

from drf_openapi.entities import VersionedSerializer


def view_config(request_serializer=None, response_serializer=None) -> Callable:
    def decorator(view_method: Callable) -> Callable:

        view_method.request_serializer = request_serializer
        view_method.response_serializer = response_serializer

        @wraps(view_method)
        def wrapper(instance, request, version, *args, **kwargs):
            if request_serializer and issubclass(request_serializer, VersionedSerializer):
                instance.request_serializer = request_serializer.get(version)
            else:
                instance.request_serializer = request_serializer

            if response_serializer and issubclass(response_serializer, VersionedSerializer):
                instance.response_serializer = response_serializer.get(version)
            else:
                instance.response_serializer = response_serializer

            return view_method(instance, request, version, *args, **kwargs)
        return wrapper
    return decorator
