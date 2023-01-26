VERSION = (3, 1, 0)

__version__ = "3.1.0"

try:
    import django
except ModuleNotFoundError:
    pass
else:
    if django.VERSION < (3, 2):
        default_app_config = "tg_react.apps.TgReactConfig"
