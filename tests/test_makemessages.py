import os
from mock import MagicMock, patch

from django.core.management import CommandError
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO


class MakeMessagesTest(TestCase):

    @patch('subprocess.call', MagicMock(return_value=1))
    def test_command_fail(self):
        out = StringIO()
        with self.settings(SITE_ROOT=os.path.dirname(os.path.dirname(__file__))), self.assertRaises(CommandError):
            call_command('makemessages', stdout=out)

    @patch('subprocess.call', MagicMock(return_value=0))
    @patch('django.core.management.commands.makemessages.Command.execute', MagicMock())
    def test_command_fail(self):
        out = StringIO()
        with self.settings(SITE_ROOT=os.path.dirname(os.path.dirname(__file__)), LOCALE_PATHS='/tmp'):
            call_command('makemessages', stdout=out)
