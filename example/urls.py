from __future__ import unicode_literals

from django.conf.urls import include, url

from django.contrib import admin

admin.autodiscover()


def test_view(request):
    pass


urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^test/', test_view, name='test_view'),
]
