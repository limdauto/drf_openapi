=====
Usage
=====

1. Quickstart
^^^^^^^^^^^^^^

.. code:: python

   # in settings.py
   INSTALLED_APPS = [
       ...
       'drf_openapi'
   ]
   REST_FRAMEWORK = {
       'DEFAULT_VERSIONING_CLASS': 'rest_framework.versioning.URLPathVersioning'
   }

   # in urls.py
   urlpatterns += [url(f'{API_PREFIX}/', include('drf_openapi.urls'))]

And voila! Your API documentation will be available at :code:`/<API_PREFIX>/schema`

2. Add schema to a view method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DRF OpenAPI support the separation of response schema and request schema on a per view method basis through the use of a `view_config` decorator

.. code:: python

   from drf_openapi.utils import view_config

   class SnippetList(APIView):
   """
   List all snippets, or create a new snippet.
   """

       @view_config(response_serializer=SnippetSerializer)
       def get(self, request, version, format=None):
           snippets = Snippet.objects.all()
           res = self.response_serializer(snippets, many=True)
           res.is_valid(raise_exception=True)
           return Response(res.validated_data)

       @view_config(request_serializer=SnippetSerializer, response_serializer=SnippetSerializer)
       def post(self, request, version, format=None):
           req = self.request_serializer(data=request.data)
           req.is_valid(raise_exception=True)
           req.save()
           res = self.response_serializer(req.data)
           res.is_valid(raise_exception=True)
           return Response(res.validated_data, status=status.HTTP_201_CREATED)


3. Add version to schema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DRF OpenAPI support schema versioning through versioning the serializers that the schema are generated from.
To make a serializer version-specific, extends :code:`VersionedSerializers`

.. code:: python

   from drf_openapi.entities import VersionedSerializers
   from rest_framework import serializers


   class SnippetSerializerV1(serializers.Serializer):
       title = serializers.CharField(required=False, allow_blank=True, max_length=100)


   class SnippetSerializerV2(SnippetSerializerV1):
       title = serializers.CharField(required=True, max_length=100)


   class SnippetSerializer(VersionedSerializers):
       """
       Changelog:

       * **v1.0**: `title` is optional
       * **v2.0**: `title` is required
       """

       VERSION_MAP = (
           ('>=1.0, <2.0', SnippetSerializerV1),
           ('>=2.0', SnippetSerializerV2),
       )


That's it. The :code:`view_config` decorator will be able to correctly determined what serializer to use based on the request version at run time.

4. Add response status code to schema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

By default, the response serializer's fields and docstring, if specified, are associated with the :code:`200` status code.
Support for error status codes is provided through the use of :code:`Meta` class in the serializer.

.. code:: python

   from rest_framework.status import HTTP_400_BAD_REQUEST

   class SnippetSerializerV1(serializers.Serializer):
       title = serializers.CharField(required=False, allow_blank=True, max_length=100)

       class Meta:
           error_status_codes = {
               HTTP_400_BAD_REQUEST: 'Bad Request'
           }

In later iteration, I will add support for sample error response.
