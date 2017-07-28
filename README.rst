===========
DRF OpenAPI
===========


.. image:: https://img.shields.io/pypi/v/drf_openapi.svg
        :target: https://pypi.python.org/pypi/drf_openapi

.. image:: https://img.shields.io/travis/limdauto/drf_openapi.svg
        :target: https://travis-ci.org/limdauto/drf_openapi

.. image:: https://readthedocs.org/projects/drf-openapi/badge/?version=latest
        :target: https://drf-openapi.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://pyup.io/repos/github/limdauto/drf_openapi/shield.svg
     :target: https://pyup.io/repos/github/limdauto/drf_openapi/
     :alt: Updates


Utilities to generate OpenAPI-compatible schema from API made with Django Rest Framework. Also use `ReDoc <https://github.com/Rebilly/ReDoc>`_ as default interface.

.. image:: https://github.com/Rebilly/ReDoc/blob/master/demo/redoc-demo.png


* Free software: MIT license
* Documentation: https://drf-openapi.readthedocs.io.

Motivation
-----------

Django Rest Framework has an `API schema generation/declaration mechanism <http://www.django-rest-framework.org/api-guide/schemas/>`_ provided by
`coreapi <http://www.coreapi.org/>`_ standard. There are a couple of problems with the current ecosystem:

- CoreAPI is not compatible out of the box with `OpenAPI <https://www.openapis.org/>`_ which is a much more popular API standard with superior tooling support, i.e. Swagger et. al.
- The OpenAPI codec (compatibility layer) that CoreAPI team provides drops / doesn't support a number of useful OpenAPI features.
- There is no support for versioning or method-specific schema.

This project was born to bridge the gap. 

Usage
----------


1. Quickstart
^^^^^^^^^^^^^^

Out of the box, DRF OpenAPI inspects all of the endpoints reigstered with Django Rest Framework (DRF) and automatically
generate documenation for them based on metadata provided by DRF and your serializer definitions.
So no need to do anything, just plug it in:

.. code:: python

   # in settings.py
   INSTALLED_APPS = [
       ...
       'drf_openapi'   
   ]
   # in urls.py
   urlpatterns += [url(f'{API_PREFIX}/', include('drf_openapi.urls'))]


And voila! Your API documentation will be available at :code:`<API_Prefix>/schema`

2. Add schema to a view method
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DRF OpenAPI support the separation of response schema and request schema on a per view method basis through the use of a `view_config` decorator

.. code:: python

   from drf_openapi.utils import view_config

   class MeEndpointSet(viewsets.ViewSet):

      @view_config(
          request_serializer=MeRequestSerializer,
          response_serializer=MeResponseSerializer,
          validate_response=True)
      def list(self, request, version) -> Response:
          # the serializers are available on the self object
          assert self.request_serializer == MeRequestSerializer
          assert self.response_serializer == MeResponseSerializer


3. Add version to schema
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

DRF OpenAPI support schema versioning through versioning the serializers that the schema are generated from.
To make a serializer version-specific, extends :code:`VersionedSerializer`

.. code:: python
   
   from drf_openapi.entities import VersionedSerializer
   from rest_framework import serializers

   class MeResponseSerializer(VersionedSerializer):
       class V1(serializers.Serializer):
           avatar = serializers.CharField(allowed_null=True)

       class V2(serialiers.Serializer):
           avatar =  serializers.CharField(allowed_null=False)
       
       VERSION_MAP = (
           '>=1.0, <2.0': V1,
           '>=2.0': V2
       )


That's it. The :code:`view_config` decorator will be able to correctly determined what serializer to use based on the request version at run time.


Features
--------

1. Schema
^^^^^^^^^^

* Add per method schema definition through inspecting serializers
* Add per serializer versioning
* Add capability to generate `response schema <https://github.com/encode/django-rest-framework/issues/4502>`_ on an endpoint.

2. OpenAPI codec
^^^^^^^^^^^^^^^^^^^^

* Return response object as defined by the response schema
* Return multiple response `status codes and messages <https://stackoverflow.com/questions/40175410/how-to-generate-list-of-response-messages-in-django-rest-swagger>`_. [TODO]

3. UI
^^^^^^^^^^

* Support different OpenAPI UIs, not just Swagger. For example, `ReDoc <https://github.com/Rebilly/ReDoc>`_.

4. Utils
^^^^^^^^^^

* A declarative machanism to provide more metadata for an API endpoint and therefore providing richer information for documentation generation.

