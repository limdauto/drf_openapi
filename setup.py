#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    'django-rest-swagger==2.1.2'
]

setup_requirements = [
    'pytest-runner',
    # TODO(limdauto): put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='drf_openapi',
    version='0.9.3',
    description="Utilities to generate OpenAPI-compatible schema from API made with Django Rest Framework",
    long_description=readme + '\n\n' + history,
    author="Lim H.",
    author_email='limdauto@gmail.com',
    url='https://github.com/limdauto/drf_openapi',
    packages=find_packages(include=['drf_openapi']),
    entry_points={
        'console_scripts': [
            'drf_openapi=drf_openapi.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="MIT license",
    zip_safe=False,
    keywords='drf_openapi',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
