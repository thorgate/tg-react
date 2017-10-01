import pytest
from django.core.exceptions import ImproperlyConfigured

from tg_react.webpack import WebpackConstants


def example_constants(context):
    return list()


invalid_constants = None


def test_default_constants():
    assert WebpackConstants.collect() == {'SITE_URL': 'http://127.0.0.1:8000', 'STATIC_URL': '/static/'}


def test_bad_config(settings):
    settings.WEBPACK_CONSTANT_PROCESSORS = None
    with pytest.raises(ImproperlyConfigured):
        WebpackConstants.collect()

    settings.WEBPACK_CONSTANT_PROCESSORS = ['tests.test_webpack_constants.example_constants']
    assert WebpackConstants.collect() == {}

    settings.WEBPACK_CONSTANT_PROCESSORS = ['tests.test_webpack_constants.invalid_constants']
    with pytest.raises(ImproperlyConfigured):
        WebpackConstants.collect()
