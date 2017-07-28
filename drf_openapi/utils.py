from functools import wraps

from typing import Callable

from drf_openapi.entities import VersionedSerializers
from rest_framework.response import Response


def view_config(request_serializer=None, response_serializer=None, validate_response=False) -> Callable:
    def decorator(view_method: Callable) -> Callable:

        view_method.request_serializer = request_serializer
        view_method.response_serializer = response_serializer

        @wraps(view_method)
        def wrapper(instance, request, version, *args, **kwargs):
            if request_serializer and issubclass(request_serializer, VersionedSerializers):
                instance.request_serializer = request_serializer.get(version)
            else:
                instance.request_serializer = request_serializer

            if response_serializer and issubclass(response_serializer, VersionedSerializers):
                instance.response_serializer = response_serializer.get(version)
            else:
                instance.response_serializer = response_serializer

            response = view_method(instance, request, version, *args, **kwargs)
            if validate_response:
                response_validator = instance.response_serializer(data=response.data)
                response_validator.is_valid(raise_exception=True)
                return Response(response_validator.validated_data)

            return response

        return wrapper
    return decorator
