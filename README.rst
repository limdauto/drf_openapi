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


Utilities to generate OpenAPI-compatible schema from API made with Django Rest Framework


* Free software: MIT license
* Documentation: https://drf-openapi.readthedocs.io.


Motivation
-----------

Django Rest Framework has an `API schema generation/declaration mechanism <http://www.django-rest-framework.org/api-guide/schemas/>`_ provided by
`coreapi <http://www.coreapi.org/>`_ standard. There are a couple of problems with the current ecosystem:

- CoreAPI is not compatible out of the box with `OpenAPI <https://www.openapis.org/>`_ which is a much more popular API standard with superior tooling support, i.e. Swagger et. al.
- The OpenAPI codec (compatibility layer) that CoreAPI team provides drops / doesn't support a number of useful OpenAPI features.

This project was born to bridge the gap. In an ideal world, which very likely will happen somewhere in 2018, we won't need this project at all
as it seems DRF + CoreAPI team, a.k.a Tom Christie, are keen on providing these supports out of the box.
In the mean time, for those who can't wait, feel free to use this package.

Features
--------

1. Schema
^^^^^^^^^^

* Add capability to generate `response schema <https://github.com/encode/django-rest-framework/issues/4502>`_ on an endpoint.
* Add first-class support for endpoint-specific versioning
* Add support for different response status codes and messages

2. OpenAPI codec
^^^^^^^^^^

* Return response object as defined by the response schema
* Return multiple response `status codes and messages <https://stackoverflow.com/questions/40175410/how-to-generate-list-of-response-messages-in-django-rest-swagger>`_.

3. UI
^^^^^^^^^^

* Support different OpenAPI UIs, not just Swagger. For example, `ReDoc <https://github.com/Rebilly/ReDoc>`_.

4. Utils
^^^^^^^^^^

* A declarative machanism to provide more metadata for an API endpoint and therefore providing richer information for documentation generation.

Examples
--------

To be added.