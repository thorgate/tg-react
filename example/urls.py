from __future__ import unicode_literals

try:
    from django.urls import re_path as url
except ImportError:
    from django.conf.urls import url

from django.contrib import admin

admin.autodiscover()


def test_view(request):
    pass


urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^test/', test_view, name='test_view'),
]
