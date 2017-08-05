# coding=utf-8
import operator
from collections import OrderedDict

import coreschema
import uritemplate
from coreapi import Link, Document, Field
from coreapi.compat import force_text
from django.db import models
from openapi_codec.encode import _get_parameters
from pkg_resources import parse_version
from rest_framework import serializers
from rest_framework.schemas import SchemaGenerator, insert_into, get_pk_description, field_to_schema


class VersionedSerializers:
    """Adapted from https://github.com/avanov/Rhetoric/ :)
    """
    OPERATORS = {
        '>': operator.gt,
        '<': operator.lt,
        '==': operator.eq,
        '>=': operator.ge,
        '<=': operator.le
    }

    """
    A map of version and serializer definition
    May be represented in the following form

    1. ``VERSION``
    2. ``==VERSION`` (the same as above)
    3. ``>VERSION``
    4. ``<VERSION``
    5. ``>=VERSION``
    6. ``<=Version``
    7. Comma-separated list of 1-7 evaluated as AND

    Must override in subclass, for example

    VERSION_MAP = (
        ('>1.3, <=1.6', MeSerializer16)
        ('>1.6', MeSerializer)
    )
    
    """
    VERSION_MAP = ()

    @classmethod
    def get(cls, request_version: str):
        for allowed_version, schema in cls.VERSION_MAP:
            distinct_versions = [version.strip() for version in allowed_version.split(',')]
            matched = True
            for distinct_version in distinct_versions:
                operation = cls.OPERATORS.get(distinct_version[:2])
                if operation:
                    # prepare cases #2, #5, #6
                    compare_with = distinct_version[2:]
                else:
                    operation = cls.OPERATORS.get(distinct_version[0])
                    if operation:
                        # prepare cases #3, #4
                        compare_with = distinct_version[1:]
                    else:
                        # prepare case #1
                        compare_with = distinct_version
                        operation = cls.OPERATORS['==']

                matched = operation(parse_version(request_version), parse_version(compare_with))
                if not matched:
                    matched = False

            if matched:
                return schema

        raise ValueError(f'Invalid request version {request_version}')


class OpenApiSchemaGenerator(SchemaGenerator):
    def __init__(self, version, title=None, url=None, description=None, patterns=None, urlconf=None):
        self.version = version
        super(OpenApiSchemaGenerator, self).__init__(title, url, description, patterns, urlconf)

    def get_schema(self, request=None, public=False):
        if self.endpoints is None:
            inspector = self.endpoint_inspector_cls(self.patterns, self.urlconf)
            self.endpoints = inspector.get_api_endpoints()

        links = self.get_links(None if public else request)
        if not links:
            return None

        url = self.url
        if not url and request is not None:
            url = request.build_absolute_uri()

        return OpenApiDocument(
            version=self.version,
            title=self.title, description=self.description,
            url=url, content=links
        )

    def get_links(self, request=None):
        """
        Return a dictionary containing all the links that should be
        included in the API schema.
        """
        links = OrderedDict()

        # Generate (path, method, view) given (path, method, callback).
        paths = []
        view_endpoints = []
        for path, method, callback in self.endpoints:
            view = self.create_view(callback, method, request)
            if getattr(view, 'exclude_from_schema', False):
                continue
            path = self.coerce_path(path, method, view)
            paths.append(path)
            view_endpoints.append((path, method, view))

        # Only generate the path prefix for paths that will be included
        if not paths:
            return None
        prefix = self.determine_path_prefix(paths)

        for path, method, view in view_endpoints:
            if not self.has_view_permissions(path, method, view):
                continue
            link = self.get_link(path, method, view, version=request.version)
            subpath = path[len(prefix):]
            keys = self.get_keys(subpath, method, view)
            try:
                insert_into(links, keys, link)
            except Exception:
                continue
        return links

    def get_serializer_doc(self, serializer):
        if serializer.__doc__ is None:
            return ''

        doc = []
        for line in serializer.__doc__.splitlines():
            doc.append(line.strip())
        return '\n'.join(doc)

    def get_link(self, path, method, view, version=None):
        fields = self.get_path_fields(path, method, view)
        fields += self.get_serializer_fields(path, method, view, version=version)
        fields += self.get_pagination_fields(path, method, view)
        fields += self.get_filter_fields(path, method, view)

        if fields and any([field.location in ('form', 'body') for field in fields]):
            encoding = self.get_encoding(path, method, view)
        else:
            encoding = None

        description = self.get_description(path, method, view)

        method_name = getattr(view, 'action', method.lower())
        method_func = getattr(view, method_name, None)

        request_serializer_class = getattr(method_func, 'request_serializer', None)
        if request_serializer_class and issubclass(request_serializer_class, VersionedSerializers):
            request_doc = self.get_serializer_doc(request_serializer_class)
            if request_doc:
                description = description + '\n\n**Request Description:**\n' + request_doc

        response_serializer_class = getattr(method_func, 'response_serializer', None)
        if response_serializer_class and issubclass(response_serializer_class, VersionedSerializers):
            res_doc = self.get_serializer_doc(response_serializer_class)
            if res_doc:
                description = description + '\n\n**Response Description:**\n' + res_doc
            response_serializer_class = response_serializer_class.get(version)

        response_schema, error_status_codes = self.get_response_object(
            response_serializer_class, method_func.__doc__) if response_serializer_class else ({}, {})

        return OpenApiLink(
            response_schema=response_schema,
            error_status_codes=error_status_codes,
            url=path.replace('{version}', self.version),  # can't use format because there may be other param
            action=method.lower(),
            encoding=encoding,
            fields=fields,
            description=description
        )

    def get_path_fields(self, path, method, view):
        """
        Return a list of `coreapi.Field` instances corresponding to any
        templated path variables.
        """
        model = getattr(getattr(view, 'queryset', None), 'model', None)
        fields = []

        for variable in uritemplate.variables(path):

            if variable == 'version':
                continue

            title = ''
            description = ''
            schema_cls = coreschema.String
            kwargs = {}
            if model is not None:
                # Attempt to infer a field description if possible.
                try:
                    model_field = model._meta.get_field(variable)
                except:
                    model_field = None

                if model_field is not None and model_field.verbose_name:
                    title = force_text(model_field.verbose_name)

                if model_field is not None and model_field.help_text:
                    description = force_text(model_field.help_text)
                elif model_field is not None and model_field.primary_key:
                    description = get_pk_description(model, model_field)

                if hasattr(view, 'lookup_value_regex') and view.lookup_field == variable:
                    kwargs['pattern'] = view.lookup_value_regex
                elif isinstance(model_field, models.AutoField):
                    schema_cls = coreschema.Integer

            field = Field(
                name=variable,
                location='path',
                required=True,
                schema=schema_cls(title=title, description=description, **kwargs)
            )
            fields.append(field)

        return fields

    def get_serializer_fields(self, path, method, view, version=None):
        """
        Return a list of `coreapi.Field` instances corresponding to any
        request body input, as determined by the serializer class.
        """
        if method not in ('PUT', 'PATCH', 'POST'):
            return []

        if not hasattr(view, 'serializer_class') and not hasattr(view, 'get_serializer_class'):
            return []

        serializer_class = view.get_serializer_class() if hasattr(view, 'get_serializer_class') \
            else view.serializer_class
        serializer = serializer_class()

        if isinstance(serializer, serializers.ListSerializer):
            return [
                Field(
                    name='data',
                    location='body',
                    required=True,
                    schema=coreschema.Array()
                )
            ]

        if not isinstance(serializer, serializers.Serializer):
            return []

        fields = []
        for field in serializer.fields.values():
            if field.read_only or isinstance(field, serializers.HiddenField):
                continue

            required = field.required and method != 'PATCH'
            field = Field(
                name=field.field_name,
                location='form',
                required=required,
                schema=field_to_schema(field),
                description=field.help_text,
            )
            fields.append(field)

        return fields

    def get_response_object(self, response_serializer_class, description):

        fields = []
        serializer = response_serializer_class()
        nested_obj = {}

        for field in serializer.fields.values():
            if isinstance(field, serializers.Serializer):
                nested_obj[field.field_name] = self.get_response_object(field.__class__, None)[0]['schema']
                nested_obj[field.field_name]['description'] = field.help_text
                continue

            fields.append(Field(
                name=field.field_name,
                location='form',
                required=field.required,
                schema=field_to_schema(field)
            ))

        res = _get_parameters(Link(fields=fields), None)

        if not res:
            if nested_obj:
                return {
                    'description': description,
                    'schema': {
                        'type': 'object',
                        'properties': nested_obj
                    }
                }, {}
            else:
                return {}, {}

        schema = res[0]['schema']
        schema['properties'].update(nested_obj)
        response_schema = {
            'description': description,
            'schema': schema
        }

        error_status_codes = {}

        response_meta = getattr(response_serializer_class, 'Meta', None)

        for status_code, description in getattr(response_meta, 'error_status_codes', {}).items():
            error_status_codes[status_code] = {'description': description}

        return response_schema, error_status_codes


class OpenApiDocument(Document):
    """OpenAPI-compliant document provides:
    - Versioning information
    """

    def __init__(self, version, url=None, title=None, description=None, media_type=None, content=None):
        super(OpenApiDocument, self).__init__(
            url=url,
            title=title,
            description=description,
            media_type=media_type,
            content=content
        )
        self._version = version

    @property
    def version(self):
        return self._version


class OpenApiLink(Link):
    """OpenAPI-compliant Link provides:
    - Schema to the response
    """

    def __init__(self, response_schema, error_status_codes,
                 url=None, action=None, encoding=None, transform=None, title=None,
                 description=None, fields=None):
        super(OpenApiLink, self).__init__(
            url=url,
            action=action,
            encoding=encoding,
            transform=transform,
            title=title,
            description=description,
            fields=fields
        )
        self._response_schema = response_schema
        self._error_status_codes = error_status_codes

    @property
    def response_schema(self):
        return self._response_schema

    @property
    def error_status_codes(self):
        return self._error_status_codes
