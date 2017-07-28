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


Generates OpenAPI-compatible schema from API made with Django Rest Framework. Use `ReDoc <https://github.com/Rebilly/ReDoc>`_ as default interface instead of Swagger.
First-class support for API versioning changelog & method-specific schema definition.

.. image:: https://github.com/Rebilly/ReDoc/blob/master/demo/redoc-demo.png


* Free software: MIT license
* Documentation: https://drf-openapi.readthedocs.io.

.. contents:: 

Background
-----------

Django Rest Framework has an `API schema generation/declaration mechanism <http://www.django-rest-framework.org/api-guide/schemas/>`_ provided by
`coreapi <http://www.coreapi.org/>`_ standard. There are a couple of problems with the current ecosystem:

- CoreAPI is not compatible out of the box with `OpenAPI <https://www.openapis.org/>`_ which is a much more popular API standard with superior tooling support, i.e. Swagger et. al.
- The OpenAPI codec (compatibility layer) that CoreAPI team provides drops / doesn't support a number of useful OpenAPI features.
- There is no support for versioning or method-specific schema.

This project was born to bridge the gap. The high-level requirements are as followed:

- Can be dropped into any existing DRF project without any code change necessary.
- Provide clear disctinction between request schema and response schema.
- Provide a versioning mechanism for each schema. Support defining schema by version range syntax, e.g. :code:`>1.0, <=2.0`
- All this information should be bound to view methods, not view classes.

It's important to stress the non-intrusiveness requirement, not least because I want to minimize what I will have to change when
DRF itself decides to support OpenAPI officially, if at all.

Design
-------------

- Schema are automatically generated from `serializers <http://www.django-rest-framework.org/api-guide/serializers/>`_
    - From here onwards, :code:`schema` and :code:`serializer` are used interchangably
- Versioned schema is supported by extending :code:`VersionedSerializer`.
- Metadata, i.e. versioning, response and request schema, are bound to a view method through the :code:`view_config` decorator.
- Automatic response validation is optionally provided :code:`view_config(response_serializer=FooSerializer, validate_response=True)`

Constraints
-------------

Currently DRF OpenAPI only supports DRF project that has `versioning <http://www.django-rest-framework.org/api-guide/versioning/#urlpathversioning>`_ enabled.
I have only tested `URLPathVersioning <http://www.django-rest-framework.org/api-guide/versioning/#urlpathversioning>`_ but I intend to suppor the full range of
versioning scheme supported by DRF.

Also the schema view is limited to staff member for now. I plan to add more granular permission very soon.

Installation
------------

.. code:: bash
   
   pip install drf_openapi

Usage
----------

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

Examples
----------

I have recreated the example in `DRF tutorial <http://www.django-rest-framework.org/tutorial/>`_ with OpenAPI schema enabled
in `examples <examples/>`_.
