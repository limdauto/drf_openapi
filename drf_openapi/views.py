# coding=utf-8
from rest_framework import response, permissions
from rest_framework.renderers import CoreJSONRenderer
from rest_framework.views import APIView

from drf_openapi.codec import OpenAPIRenderer, SwaggerUIRenderer
from drf_openapi.entities import OpenApiSchemaGenerator


class SchemaView(APIView):
    renderer_classes = (CoreJSONRenderer, SwaggerUIRenderer, OpenAPIRenderer)
    permission_classes = (permissions.IsAdminUser,)
    url = ''
    title = 'API Documentation'

    def get(self, request, version):
        generator = OpenApiSchemaGenerator(
            version=version,
            url=self.url,
            title=self.title
        )
        return response.Response(generator.get_schema(request))
