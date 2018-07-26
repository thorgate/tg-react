from __future__ import unicode_literals

from django.contrib import admin

admin.autodiscover()


urlpatterns = [
    admin.site.urls,
]
