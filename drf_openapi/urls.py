from django.conf import settings
from django.conf.urls import url, include

from drf_openapi.views import get_schema_view
urlpatterns = [
    url(f'schema/$', get_schema_view(url=settings.DOMAIN, title="Memrise API"), name='api_schema')
]