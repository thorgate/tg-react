import json
import unittest

from tg_react.language import DjangoLocaleData


class LanguagesTestCase(unittest.TestCase):

    def assertForLanguage(self, language, plural_form=None, packages=None):
        locale_data_generator = DjangoLocaleData(packages=packages)
        languages, languages_data = locale_data_generator.collect_translations()

        self.assertTrue(language in languages.keys())
        self.assertTrue(language in languages_data.keys())

        locale_data = json.loads(languages_data.get(language))
        header_data = locale_data.get('')

        # Remove diff unfriendly values
        header_data.pop('po-revision-date')
        header_data.pop('pot-creation-date')

        self.assertDictEqual(header_data, {
            'mime-version': '1.0',
            'last-translator': 'Automatic <hi@thorgate.eu>',
            'x-generator': 'Python',
            'language': language,
            'lang': language,
            'content-transfer-encoding': '8bit',
            'project-id-version': 'Example v0.0.1',
            'domain': 'djangojs',
            'report-msgid-bugs-to': '',
            'content-type': 'text/plain; charset=UTF-8',
            'plural-forms': plural_form,
            'language-team': 'Automatic <hi@thorgate.eu>'
        })

        language_key = language.upper()
        self.assertEqual(locale_data.get('Dummy test string'), '%s: Dummy test string' % language_key)
        self.assertEqual(locale_data.get('test\x04Dummy test string'), '%s: Dummy test string' % language_key)
        self.assertEqual(
            locale_data.get('Dummy test string Dummy test string'),
            '%s: Dummy test string Dummy test string' % language_key
        )
        self.assertEqual(
            locale_data.get('There is %s more waybill'), [
                '%s: There is %%s more waybill' % language_key, '%s: There are %%s more waybills' % language_key
            ]
        )
        self.assertEqual(
            locale_data.get('list\x04There is %(waybillCount)s more waybill'), [
                '%s: There is %%(waybillCount)s more waybill' % language_key,
                '%s: There are %%(waybillCount)s more waybills' % language_key,
            ]
        )

    def test_for_english(self):
        self.assertForLanguage('en')

    def test_for_estonian(self):
        self.assertForLanguage('et', plural_form='(n != 1)')

    def test_for_russian(self):
        self.assertForLanguage(
            'ru',
            plural_form='(n%10==1 && n%100!=11 ? 0 : n%10>=2 && n%10<=4 && (n%100<12 '
            '|| n%100>14) ? 1 : n%10==0 || (n%10>=5 && n%10<=9) || (n%100>=11 && n%100<=14)? 2 : 3)',
        )

    def test_with_package_define(self):
        self.assertForLanguage('en', packages='django.contrib.admin')
