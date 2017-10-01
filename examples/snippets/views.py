from drf_openapi.utils import view_config
from snippets.models import Snippet
from snippets.serializers import SnippetSerializer
from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


_FAKE_SNIPPETS = [
    {
        'id': 1,
        'title': 'foo',
        'code': 'print("hello")',
        'language': {'name': 'python'},
        'lines': [1, 2, 3],
        'example_projects': [{
            'project_name': 'drf_openapi',
            'github_repo': 'https://github.com/limdauto/drf_openapi/'
        }]
    }
]


class SnippetList(APIView):
    """
    List all snippets, or create a new snippet.
    """

    @view_config(response_serializer=SnippetSerializer)
    def get(self, request, version, format=None):
        res = self.response_serializer(data=_FAKE_SNIPPETS, many=True)
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
