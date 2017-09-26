from django.conf.urls import url
from django.contrib.admin.views.decorators import staff_member_required

from drf_openapi.views import get_schema_view
urlpatterns = [
    url('schema/$', staff_member_required(get_schema_view(url='', title="API Documentation")), name='api_schema')
]
