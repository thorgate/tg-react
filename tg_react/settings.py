from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

try:
    from django.utils.module_loading import import_string

except ImportError:
    from django.utils.module_loading import import_by_path as import_string


def get_user_signup_fields():
    return getattr(settings, 'TGR_USER_SIGNUP_FIELDS', ['name', ])


def exclude_fields_from_user_details():
    return getattr(settings, 'TGR_EXCLUDED_USER_FIELDS', [])


def _user_extra_fields(validate=False):
    fields = getattr(settings, 'TGR_USER_EXTRA_FIELDS', {})

    if validate:
        if not isinstance(fields, dict):
            raise ImproperlyConfigured("settings.TGR_USER_EXTRA_FIELDS must be a dict")

    res = {}
    for name, conf in fields.items():
        if validate and not isinstance(conf, (str, list)):
            raise ImproperlyConfigured("settings.TGR_USER_EXTRA_FIELDS value must be a module path or list[path, kwargs]")

        path = conf if not isinstance(conf, list) else conf[0]
        kwargs = {} if not isinstance(conf, list) else conf[1] or {}

        res[name] = [import_string(path), kwargs]

    return res


def get_password_recovery_url():
    return getattr(settings, 'TGR_PASSWORD_RECOVERY_URL', '/reset_password/%s')


def get_post_login_handler():
    return getattr(settings, 'TGR_POST_LOGIN_HANDLER', None)


def get_post_logout_handler():
    return getattr(settings, 'TGR_POST_LOGOUT_HANDLER', None)


def configure():
    if not isinstance(exclude_fields_from_user_details(), (list, tuple)):
        raise ImproperlyConfigured("settings.TGR_EXCLUDED_USER_FIELDS must be list|tuple")

    if not isinstance(get_user_signup_fields(), (list, tuple)):
        raise ImproperlyConfigured("settings.TGR_USER_SIGNUP_FIELDS must be list|tuple")

    handler = get_post_login_handler()
    if handler is not None and not isinstance(handler, str):
        raise ImproperlyConfigured("settings.TGR_POST_LOGIN_HANDLER must be module path")

    handler = get_post_logout_handler()
    if handler is not None and not isinstance(handler, str):
        raise ImproperlyConfigured("settings.TGR_POST_LOGOUT_HANDLER must be module path")

    recovery_url = get_password_recovery_url()
    if not isinstance(recovery_url, str):
        raise ImproperlyConfigured("settings.TGR_PASSWORD_RECOVERY_URL must be str")

    try:
        t = recovery_url % 'TEST'
    except TypeError:
        raise ImproperlyConfigured(
            "settings.TGR_PASSWORD_RECOVERY_URL must contain a string "
            "formatting token for base64 encoded data")


configure()
user_extra_fields = _user_extra_fields(validate=True)
