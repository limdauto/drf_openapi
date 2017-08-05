# coding=utf-8
"""Adapted from https://github.com/core-api/python-openapi-codec/blob/master/openapi_codec/encode.py
and https://github.com/marcgibbons/django-rest-swagger/blob/master/rest_framework_swagger/renderers.py
"""
import json
from collections import OrderedDict
from typing import Dict, List, Optional

from coreapi import Document
from coreapi.compat import urlparse, force_bytes
from openapi_codec import OpenAPICodec as _OpenAPICodec
from openapi_codec.encode import _get_links, _get_parameters
from openapi_codec.utils import get_method, get_encoding
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework_swagger.renderers import OpenAPIRenderer as _OpenAPIRenderer, \
    SwaggerUIRenderer as _SwaggerUIRenderer

from drf_openapi.entities import OpenApiLink, OpenApiDocument


class OpenAPICodec(_OpenAPICodec):
    def encode(self, document: OpenApiDocument, extra=None, **options) -> str:
        if not isinstance(document, Document):
            raise TypeError('Expected a `coreapi.Document` instance')

        data = _generate_openapi_object(document)
        if isinstance(extra, dict):
            data.update(extra)

        return force_bytes(json.dumps(data))


class OpenAPIRenderer(_OpenAPIRenderer):

    def render(self, data: OpenApiDocument, accepted_media_type: Optional[str] = None,
               renderer_context: Optional[Dict] = None) -> str:
        if renderer_context['response'].status_code != status.HTTP_200_OK:
            return JSONRenderer().render(data)
        extra = self.get_customizations()

        return OpenAPICodec().encode(data, extra=extra)


class SwaggerUIRenderer(_SwaggerUIRenderer):
    template = 'drf_openapi/index.html'


def _generate_openapi_object(document: OpenApiDocument) -> OrderedDict:
    """
    Generates root of the Swagger spec.
    """
    parsed_url = urlparse.urlparse(document.url)

    swagger = OrderedDict()

    swagger['swagger'] = '2.0'
    swagger['info'] = OrderedDict()
    swagger['info']['title'] = document.title
    swagger['info']['description'] = document.description
    swagger['info']['version'] = document.version

    if parsed_url.netloc:
        swagger['host'] = parsed_url.netloc
    if parsed_url.scheme:
        swagger['schemes'] = [parsed_url.scheme]

    swagger['paths'] = _get_paths_object(document)

    return swagger


def _get_paths_object(document: Document) -> OrderedDict:
    paths = OrderedDict()

    links = _get_links(document)

    for operation_id, link, tags in links:
        if link.url not in paths:
            paths[link.url] = OrderedDict()

        method = get_method(link)
        operation = _get_operation(operation_id, link, tags)
        paths[link.url].update({method: operation})

    return paths


def _get_operation(operation_id: str, link: OpenApiLink, tags: List) -> Dict:
    encoding = get_encoding(link)
    description = link.description.strip()
    # summary = description.splitlines()[0] if description else None
    summary = link.url

    operation = {
        'operationId': operation_id,
        'responses': _get_responses(link),
        'parameters': _get_parameters(link, encoding)
    }

    if description:
        operation['description'] = description
    if summary:
        operation['summary'] = summary
    if encoding:
        operation['consumes'] = [encoding]
    if tags:
        operation['tags'] = tags
    return operation


def _get_responses(link: OpenApiLink) -> Dict:
    """ Returns an OpenApi-compliant response
    """
    template = link.response_schema
    template.update({'description': 'Success'})
    res = {200: template}
    res.update(link.error_status_codes)
    return res
