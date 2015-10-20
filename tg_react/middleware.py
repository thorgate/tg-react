from django.conf import settings
from django.utils import translation
from django.utils.cache import patch_vary_headers


class LocaleMiddleware(object):
    """
    This is a very simple middleware that parses a request
    and decides what translation object to install in the current
    thread context depending on the selected language.

    This also allows us to update the language cookie whenever our api endpoint is used.
    """

    def get_language_for_user(self, request):
        if request.user.is_authenticated() and hasattr(request.user, 'language'):
            return getattr(request.user, 'language')

        return translation.get_language_from_request(request)

    def process_request(self, request):
        if request.META.get('HTTP_ACCEPT_LANGUAGE', None) is not None:
            del request.META['HTTP_ACCEPT_LANGUAGE']

        translation.activate(self.get_language_for_user(request))
        request.LANGUAGE_CODE = translation.get_language()

    def process_response(self, request, response):
        language = getattr(request, 'update_language_cookie', False)

        if language:
            if request.user.is_authenticated() and hasattr(request.user, 'language'):
                language = getattr(request.user, 'language')

            else:
                language = language or request.LANGUAGE_CODE

            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, language,
                                max_age=settings.LANGUAGE_COOKIE_AGE,
                                path=settings.LANGUAGE_COOKIE_PATH,
                                domain=settings.LANGUAGE_COOKIE_DOMAIN)

        patch_vary_headers(response, ("Accept-Language",))
        response["Content-Language"] = translation.get_language()
        translation.deactivate()
        return response
