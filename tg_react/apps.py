from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

from .settings import *  # NOQA: configure


class TgReactConfig(AppConfig):
    name = 'tg_react'
    verbose_name = _('Tg react')
