from django.http.response import HttpResponse
from django.urls import re_path, include

from django.contrib import admin

admin.autodiscover()


def test_view(request):
    return HttpResponse("Hello from test_view")


urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^test/", test_view, name="test_view"),
    re_path(r"api/", include("tg_react.api.accounts.urls")),
]
