import json

from django.conf import settings
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder

from tg_react.webpack import WebpackConstants


class Command(BaseCommand):
    help = 'Output all configured constants as json'

    def add_arguments(self, parser):
        parser.add_argument('-p', '--print', action='store_true', help='Only output to stdout')

    def handle(self, *args, **options):
        output = json.dumps(WebpackConstants.collect(), cls=DjangoJSONEncoder, indent=4 if settings.DEBUG else None)

        if options['print']:
            self.stdout.write(output)

        else:
            self.stdout.write('Writing constants to constants.json')

            with open('constants.json', 'w+') as handle:
                handle.write(output)
