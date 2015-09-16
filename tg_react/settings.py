from django.core.exceptions import ImproperlyConfigured
from django.conf import settings


def get_user_model_name_fields():
    return getattr(settings, 'TGR_USER_NAME_FIELDS', ['name'])


def exclude_fields_from_user_details():
    return getattr(settings, 'TGR_EXCLUDED_USER_FIELDS', [])


def configure():
    excluded_fields = exclude_fields_from_user_details()
    if not isinstance(excluded_fields, (list, tuple)):
        raise ImproperlyConfigured(u"settings.TGR_EXCLUDED_USER_FIELDS must be list|tuple")

    user_model_name_fields = get_user_model_name_fields()
    if not isinstance(user_model_name_fields, (list, tuple)):
        raise ImproperlyConfigured(u"settings.TGR_USER_NAME_FIELDS must be list|tuple")


configure()
