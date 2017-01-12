import itertools
import json
import logging
import os
import re
import six
import django

from django.utils import timezone, _os, translation
from django.utils.encoding import force_str

from django.conf import settings


def get_plural_forms(locale):
    plural_forms_re = re.compile(r'^"Plural-Forms: (?P<value>.+?)\\n"\s*$', re.MULTILINE | re.DOTALL)
    django_dir = os.path.normpath(os.path.join(os.path.dirname(_os.upath(django.__file__))))

    django_po = os.path.join(django_dir, 'conf', 'locale', locale, 'LC_MESSAGES', 'django.po')
    if os.path.exists(django_po):
        with open(django_po, 'r', encoding='utf-8') as fp:
            m = plural_forms_re.search(fp.read())
        if m:
            return force_str(m.group('value')).strip().replace('"\n"', '')

    return 'nplurals=2; plural=(n != 1);'


def get_messages():
    try:
        from tg_react_tmp_i18n import all_messages

        result = all_messages()

    except ImportError:
        logging.warning('Did not find `tg_react_tmp_i18n.py` have you executed makemessages/compilemessages?')
        result = {}

    return result


def make_header(locale):
    now = timezone.now().isoformat()

    return {
        "po-revision-date": now,
        "mime-version": "1.0",
        "last-translator": "Automatic <hi@thorgate.eu>",
        "x-generator": "Python",
        "language": locale,
        "lang": locale,
        "content-transfer-encoding": "8bit",
        "project-id-version": "1.0.0",
        "pot-creation-date": now,
        "domain": "django",
        "report-msgid-bugs-to": "",
        "content-type": "text/plain; charset=UTF-8",
        "plural-forms": get_plural_forms(locale),
        "language-team": "Automatic <hi@thorgate.eu>"
    }


def collect_translations():
    languages = {}
    locale_data = {}
    js_messages = get_messages()

    for language_code, label in settings.LANGUAGES:
        languages[language_code] = '%s' % label

        # Add the meta object
        locale_data[language_code] = {}
        locale_data[language_code][""] = make_header(language_code)

        with translation.override(language_code):
            # Next code is largely taken from Django 1.10 djangojs logic @ django.views.i18n get_javascript_catalog
            pdict = {}
            maxcnts = {}
            trans = translation._trans.catalog()
            trans_cat = trans._catalog
            trans_fallback_cat = trans._fallback._catalog if trans._fallback else {}

            for key, value in itertools.chain(six.iteritems(trans_cat), six.iteritems(trans_fallback_cat)):
                # We only need to add string once into locale_data, this is why we check if key or msgid already
                # exists in the locale_data. Not doing this may result in incorrect translation strings from other
                # languages overwriting the correct ones.
                if isinstance(key, six.string_types):
                    if key not in js_messages.keys() or key in locale_data[language_code]:
                        continue
                    locale_data[language_code][key] = [value]
                elif isinstance(key, tuple):
                    msgid = key[0]
                    if msgid not in js_messages.keys():
                        continue
                    cnt = key[1]
                    maxcnts[msgid] = max(cnt, maxcnts.get(msgid, 0))
                    # In case of plurals the previously described logic does not work. Then we need to
                    # check if plural form already exists in translations.
                    if msgid not in pdict:
                        pdict.setdefault(msgid, {})[cnt] = value
                    elif cnt not in pdict[msgid]:
                        pdict.setdefault(msgid, {})[cnt] = value
                else:
                    raise TypeError(key)

            for k, v in pdict.items():
                locale_data[language_code][k] = [v.get(i, '') for i in range(maxcnts[k] + 1)]

    for key, value in locale_data.items():
        locale_data[key] = json.dumps(value)

    return languages, locale_data


def constants(context):
    all_languages, locale_data = collect_translations()

    return {
        'LANGUAGE_CODE': settings.LANGUAGE_CODE,
        'LANGUAGE_COOKIE_NAME': settings.LANGUAGE_COOKIE_NAME,
        'LANGUAGES': all_languages,
        'LOCALE_DATA': locale_data,
    }
