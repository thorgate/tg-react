from django.conf import settings
from django.core.exceptions import ImproperlyConfigured


try:
    from django.utils.module_loading import import_string

except ImportError:
    from django.utils.module_loading import import_by_path as import_string


class WebpackConstants(object):
    @classmethod
    def get_constant_processors(cls):
        processors = getattr(settings, 'WEBPACK_CONSTANT_PROCESSORS', ['tg_react.webpack.default_constants'])

        if not isinstance(processors, (list, tuple)):
            raise ImproperlyConfigured('WEBPACK_CONSTANT_PROCESSORS must be a list or tuple')

        return processors

    @classmethod
    def collect(cls):
        """ Load all constant generators from settings.WEBPACK_CONSTANT_PROCESSORS
            and concat their values.
        """
        constants = {}

        for method_path in WebpackConstants.get_constant_processors():
            method = import_string(method_path)

            if not callable(method):
                raise ImproperlyConfigured('Constant processor "%s" is not callable' % method_path)

            result = method(constants)

            if isinstance(result, dict):
                constants.update(result)

        return constants


def default_constants(context):
    return {
        'SITE_URL': settings.SITE_URL,
        'STATIC_URL': settings.STATIC_URL,
    }
