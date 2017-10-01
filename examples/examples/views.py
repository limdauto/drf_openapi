from rest_framework import permissions

from drf_openapi.views import SchemaView


class MySchemaView(SchemaView):
    permission_classes = (permissions.AllowAny, )
