# coding=utf-8
from rest_framework import response
from rest_framework.decorators import api_view, renderer_classes
from rest_framework.renderers import CoreJSONRenderer

from drf_openapi.codec import OpenAPIRenderer, SwaggerUIRenderer
from drf_openapi.entities import OpenApiSchemaGenerator


def get_schema_view(url, title):

    @api_view()
    @renderer_classes([CoreJSONRenderer, SwaggerUIRenderer, OpenAPIRenderer])
    def schema_view(request, version):
        generator = OpenApiSchemaGenerator(
            version=version,
            url=url,
            title=title
        )
        return response.Response(generator.get_schema(request))

    return schema_view
