import csv

from django.core.management.base import BaseCommand

from acacia.meetnet.models import MonFile
from datetime import timedelta
from django.core.exceptions import ObjectDoesNotExist
import pytz
from acacia.meetnet.util import moncorrect

class Command(BaseCommand):
    args = ''
    help = 'Corrigeer voor drift per meetronde (monfile)'
    
    def add_arguments(self, parser):
        parser.add_argument('-f','--file',
                action='store',
                dest = 'fname',
                default = None,
                help='CSV file met resultaten van check_hand met extra kolom "corrigeren?"'
        )

    def handle(self, *args, **options):
        # tolerance for interpolation = 4 hours
        tolerance = timedelta(hours=4)
        # default time zone is Dutch Wintertime
        tz = pytz.timezone('Etc/GMT-1')
        control = options.get('fname')
        if not control:
            raise Exception('control file missing')
        with open(control,'r') as f:
            reader = csv.DictReader(f, delimiter=',')
            for row in reader:
                if row['correct?'] == 'TRUE' and row['KRW'] != '#N/A':
                    filename = row['monfile']
                    print filename
                    try:
                        monfile = MonFile.objects.get(name__iexact=filename)
                    except ObjectDoesNotExist:
                        print 'Monfile not found'
                        continue
                    
                    corrected = moncorrect(monfile, tolerance, tz)
                    if corrected:
                        screen = monfile.source.screen
                        if screen.logger_levels != corrected:
                            screen.logger_levels = corrected
                            screen.save()
