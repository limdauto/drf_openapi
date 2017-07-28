from django.conf.urls import url, include

from drf_openapi.views import get_schema_view
urlpatterns = [
    url(f'schema/$', get_schema_view(url='', title="API Documentation"), name='api_schema')
]