import os
import re
import subprocess

from django.conf import settings
from django.core.management.base import CommandError, BaseCommand

from ...settings import get_static_dir


class Command(BaseCommand):
    help = 'Parses all js/jsx files and generates a python ' \
           'file containing gettext calls from it. Then runs ' \
           'the original makemessages command for all locales'

    def add_arguments(self, parser):
        parser.add_argument('-t', '--types', dest='file_types', default='\.jsx?$')
        parser.add_argument('-d', '--dir', dest='directory', default=','.join(get_static_dir()))
        parser.add_argument('-i', '--ignore', dest='ignore', default='bower_components,node_modules,build')

    @staticmethod
    def has_dir(path, dirs):
        for directory in dirs:
            if directory in path:
                return True

        return False

    def handle(self, *args, **options):
        out_path = os.path.join(settings.SITE_ROOT, 'tg_react_tmp_i18n.py')

        self.stdout.write('Generating python file from react files')
        self.stdout.write('    Pattern: %s' % options['file_types'])
        self.stdout.write('    Ignore: %s' % options['ignore'])
        self.stdout.write('    Directories: %s' % options['directory'])
        self.stdout.write('    Out path: %s' % out_path)

        options['ignore'] = options['ignore'].split(',')
        options['directory'] = options['directory'].split(',')

        if not options['file_types']:
            raise CommandError('file types not specified')

        if not options['ignore']:
            raise CommandError('ignore not specified')

        if not options['directory']:
            raise CommandError('directory not specified')

        result_files = []

        for folder in options['directory']:
            for root, dirs, files in os.walk(folder):
                for name in files:
                    full_path = os.path.join(root, name)

                    if name == 'i18n.js':
                        continue

                    if full_path:
                        if self.has_dir(full_path, options['ignore']):
                            continue

                        if re.search(options['file_types'], full_path):
                            result_files.append(full_path)

        # Run the node.js script to extract messages from js code
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'extract-js-i18n.js')
        node_environ = dict(os.environ)
        node_environ['NODE_PATH'] = node_environ.get('NODE_PATH', '') + ':' + os.path.join(settings.SITE_ROOT, 'node_modules')
        ret_code = subprocess.call(['node', script_path, out_path] + result_files, cwd=settings.SITE_ROOT, env=node_environ)
        if ret_code:
            self.stderr.write("Extraction of JS messages failed")
            self.stderr.write("Ensure that 'node' is in the PATH and you have 'babylon' and 'babel-traverse' packages installed")
            raise CommandError('Extraction of JS messages failed')

        self.stdout.write('Generation complete')
        self.stdout.write('')
        self.stdout.write('Temporary file generated')
        self.stdout.write('Manually run makemessages to generate PO files')
        self.stdout.write('')
