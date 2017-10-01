from django.conf.urls import url

from drf_openapi.views import SchemaView

urlpatterns = [
    url('schema/$', SchemaView.as_view(title='My custom API schema title'), name='api_schema')
]
