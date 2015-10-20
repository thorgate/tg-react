import os
import re

from collections import defaultdict
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.core.management.commands import makemessages

from ...settings import get_static_dir


class ParseJsTranslations(object):
    ALL_FUNCS = [
        'dcgettext',
        'dgettext',

        'dcngettext',
        'dngettext',
        'ngettext',

        'dcnpgettext',
        'dnpgettext',
        'npgettext',
        'dpgettext',
        'pgettext',

        'gettext',
    ]

    DISABLED_FUNCS = {
        'dgettext',
        'dcgettext',
        'dngettext',
        'dcngettext',
        'dpgettext',
        'dcnpgettext',
    }

    def __init__(self, contents, file_name):
        self.file_name = file_name
        self.contents = contents.replace('\n', '').replace('\r', '')
        self.results = defaultdict(list)
        self.raw = []

    @staticmethod
    def find_all(needle, haystack):
        pos = 0
        while pos < len(haystack):
            pos = haystack.find(needle, pos)
            if pos == -1:
                break

            yield pos
            pos += len(needle)

    def parse(self):
        self.results = defaultdict(list)

        contents = self.contents
        for func in self.ALL_FUNCS:
            for pos in list(self.find_all(func, contents)):
                out = ''
                braces = 0
                c = '1'
                pp = pos + len(func)

                while c and pp < len(contents):
                    c = contents[pp]
                    out += c
                    pp += 1

                    if c == '(':
                        braces += 1
                    elif c == ')':
                        braces -= 1

                        if braces == 0:
                            break

                out = out.strip()
                if func in self.DISABLED_FUNCS:
                    raise ValueError('%s is not supported by Django: [%s %s]' % (func, func, out))

                # If not a function call, lets skip this
                if not out or out[0] != '(':
                    continue

                out, raw = self.clean_args(out, func)

                self.results[func].append(out)

                if raw is not None:
                    self.raw.append(raw)

                # Strip out function name from source
                #  Note: Replacing with equal length of star characters, since we want to keep the calculated positions
                contents = contents[:pos] + ('*' * len(func)) + contents[pos + len(func):]

        self.results = dict(self.results)

    def clean_args(self, out, fn):
        args = out.strip('()').split(',')

        fixed_args = []
        signature = (self.file_name, fn, out)

        for i, arg in enumerate(args):
            arg = arg.strip()

            start = arg[0]
            end = arg[-1]

            if start == '`' or end == '`':
                raise ValueError('I18N calls may not contain ES6 templates: %s: %s %s' % signature)

            if start not in ['"', "'"] or end not in ['"', "'"]:
                if fn == 'ngettext' and i == 2:
                    arg = '_number'

                elif fn == 'npgettext' and i == 3:
                    arg = '_number'

                else:
                    raise ValueError('I18N calls may not contain variables: %s: %s %s' % signature)

            fixed_args.append(arg)

        return '(%s)' % (', '.join(fixed_args)), RawCall(fn, fixed_args)


class RawCall(object):
    def __init__(self, func, args):
        self.fn = func

        self.raw_args = args
        self.args = [x.strip('\'"') for x in args]

    def __hash__(self):
        return hash(self.repr)

    @property
    def repr(self):
        return '%s(%s)' % (self.fn, ', '.join(self.args))

    def __eq__(self, other):
        return self.repr == other.repr

    def prep_value(self):
        if self.fn == 'gettext':
            return self.args[0], self.with_call([self.args[0], ])
        elif self.fn == 'pgettext':
            return '%s\u0004%s' % tuple(self.args), self.with_call([self.args[1], ], context=self.args[0])
        elif self.fn == 'ngettext':
            return self.args[0], self.with_call([self.args[0], self.args[1]])
        elif self.fn == 'npgettext':
            return '%s\u0004%s' % (self.args[0], self.args[1]), self.with_call([self.args[1], self.args[2]], context=self.args[0])

    def with_call(self, parts, context=None):
        calls = []

        for i, part in enumerate(parts):
            if self.fn in ['ngettext', 'npgettext']:
                call = [parts[0], parts[1], i+1]

                if context is not None:
                    call.insert(0, context)

            elif context is not None:
                call = [context, part]

            else:
                call = [part]

            calls.append(call)

        return ["%s(%s)" % (self.fn, ", ".join(["'%s'" % y if y not in [1, 2] else str(y) for y in x])) for x in calls]


class PythonTranslationFile(object):
    def __init__(self, the_calls, raw_calls):
        self.calls = the_calls
        self.raw_calls = raw_calls

    def contents(self):
        content = [
            'from django.utils.translation import gettext, pgettext, ngettext, npgettext',
            '',
            '',
            'def all_messages():',
            '    return {'
        ]

        for raw in self.raw_calls:
            key, args = raw.prep_value()
            content.append("        '%s': [" % key)

            for call in args:
                content.append("            %s," % call)

            content.append("        ],")

        content.append('    }')
        content.append('')

        return "\r\n".join(content)


class Command(BaseCommand):
    help = 'Parses all js/jsx files and generates a python ' \
           'file containing gettext calls from it. Then runs ' \
           'the original makemessages command for all locales'

    option_list = BaseCommand.option_list + (
        make_option(
            '-t', '--types', dest='file_types', default='\.jsx?$',
        ),
        make_option(
            '-d', '--dir', dest='directory', default=','.join(get_static_dir()),
        ),
        make_option(
            '-i', '--ignore', dest='ignore', default='bower_components,node_modules,build',
        ),
    )

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

        all_calls = defaultdict(list)
        raw_calls = []

        for file_path in result_files:
            with open(file_path) as handle:
                contents = handle.read()

                parser = ParseJsTranslations(contents, os.path.basename(file_path))
                parser.parse()

                for func, calls in parser.results.items():
                    for call in calls:
                        all_calls[func].append(call)

                raw_calls += parser.raw

                handle.close()

        # Remove duplicates
        raw_calls = list(set(raw_calls))

        with open(out_path, 'w+') as handle:
            handle.write(PythonTranslationFile(dict(all_calls), raw_calls).contents())

            handle.close()

        self.stdout.write('Generation complete')
        self.stdout.write('')
        self.stdout.write('Executing original makemessages for all enabled locales')
        self.stdout.write('')

        makemessages_opts = {
            'exclude': [],
            'locale': list(dict(settings.LANGUAGES).keys()),
            'verbosity': 1,
            'ignore_patterns': [],
            'use_default_ignore_patterns': True,
            'domain': 'django',
            'extensions': ['html', 'txt', 'py'],
        }

        # Call makemessages
        makemessages.Command().execute(**makemessages_opts)

        self.stdout.write('')
        self.stdout.write('Executing original makemessages: Complete')
        self.stdout.write('')
