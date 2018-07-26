from __future__ import unicode_literals

import re
import unittest
import django

from distutils.version import LooseVersion
from django.core.exceptions import ImproperlyConfigured

from tg_react.apiurls import flatten_urls, tokenize_pattern


class FlattenUrlsTestCase(unittest.TestCase):
    maxDiff = None

    def test_url_flatten(self):
        expected_urls_dict = {
            'admin::authGroupAdd': 'admin/auth/group/add/',
            'admin::authGroupChange': 'admin/auth/group/${arg0}/change/',
            'admin::authGroupChangelist': 'admin/auth/group/',
            'admin::authGroupDelete': 'admin/auth/group/${arg0}/delete/',
            'admin::authGroupHistory': 'admin/auth/group/${arg0}/history/',
            'admin::authUserAdd': 'admin/auth/user/add/',
            'admin::authUserChange': 'admin/auth/user/${arg0}/change/',
            'admin::authUserChangelist': 'admin/auth/user/',
            'admin::authUserDelete': 'admin/auth/user/${arg0}/delete/',
            'admin::authUserHistory': 'admin/auth/user/${arg0}/history/',
            'admin::authUserPasswordChange': 'admin/auth/user/${arg0}/password/',
            'admin:appList': 'admin/${app_label}/',
            'admin:index': 'admin/',
            'admin:jsi18n': 'admin/jsi18n/',
            'admin:login': 'admin/login/',
            'admin:logout': 'admin/logout/',
            'admin:passwordChange': 'admin/password_change/',
            'admin:passwordChangeDone': 'admin/password_change/done/',
            'admin:viewOnSite': 'admin/r/${content_type_id}/${object_id}/',
            'testView': 'test/',
        }

        # Django 1.8 and lower have slightly different admin urls
        if LooseVersion(django.get_version()) < LooseVersion("1.9"):
            expected_urls_dict.update({
                'admin::authGroupChange': 'admin/auth/group/${arg0}/',
                'admin::authUserChange': 'admin/auth/user/${arg0}/',
            })

        if LooseVersion(django.get_version()) == LooseVersion("2.0"):
            expected_urls_dict.update({
                'admin::authGroupAutocomplete': 'admin/auth/group/autocomplete/',
                'admin::authGroupChange': 'admin/auth/group/${object_id}/change/',
                'admin::authGroupDelete': 'admin/auth/group/${object_id}/delete/',
                'admin::authGroupHistory': 'admin/auth/group/${object_id}/history/',
                'admin::authUserAutocomplete': 'admin/auth/user/autocomplete/',
                'admin::authUserChange': 'admin/auth/user/${object_id}/change/',
                'admin::authUserDelete': 'admin/auth/user/${object_id}/delete/',
                'admin::authUserHistory': 'admin/auth/user/${object_id}/history/',
                'admin::authUserPasswordChange': 'admin/auth/user/${id}/password/',
            })

        self.assertEqual(flatten_urls('example.urls', None), expected_urls_dict)

    def test_url_flatten_invalid_conf(self):
        with self.assertRaises(ImproperlyConfigured):
            flatten_urls('example.invalid_urls', None)

    def test_url_flatten_resolver(self):
        self.assertEqual(flatten_urls('example.resolver_urls.urlpatterns', None), {})

    def test_tokenize_pattern(self):
        self.assertEqual(tokenize_pattern(re.compile(r'^(.*)/$')), '${arg0}/')
        self.assertEqual(tokenize_pattern(re.compile(r'^(?P<test>.*)/test/$')), '${test}/test/')
        self.assertEqual(tokenize_pattern(None), None)
