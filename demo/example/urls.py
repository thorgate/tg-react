from django.http.response import HttpResponse
from django.urls import re_path, include
from django.utils import translation

from django.contrib import admin

admin.autodiscover()


def test_view(request):
    return HttpResponse("Hello from test_view")


def test_language_view(request):
    return HttpResponse(f"current_language: {translation.get_language()}")


urlpatterns = [
    re_path(r"^admin/", admin.site.urls),
    re_path(r"^test/", test_view, name="test_view"),
    re_path(r"^test-language/", test_language_view, name="test_language_view"),
    re_path(r"api/", include("tg_react.api.accounts.urls")),
]
