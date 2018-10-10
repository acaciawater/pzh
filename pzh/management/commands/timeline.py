'''
Created on Jul 20, 2017

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Screen
import datetime

class Command(BaseCommand):
    args = ''
    help = 'maak timeline van metingen'
                        
    def add_arguments(self, parser):
        parser.add_argument('-b', '--begin',
                action='store',
                dest = 'begin',
                default = 2017,
                help = 'first year')

        parser.add_argument('-e', '--end',
                action='store',
                dest = 'end',
                default = 2017,
                help = 'last year')

    def handle(self, *args, **options):
        first = datetime.date(int(options.get('begin')),1,1)
        last = datetime.date(int(options.get('end')),12,31)
        for s in Screen.objects.order_by('well','nr'):
            query = s.loggerpos_set.filter(end_date__gt=first,start_date__lt=last).order_by('start_date')
            empty = True
            for lp in query:
                start = lp.start_date.date()
                end = lp.end_date.date()
                if empty:
                    d1 = start
                    d2 = end
                    empty = False
                    if d1 > first:
                        print unicode(s), first, d1, 'ontbreekt'
                else:
                    if start == d2:
                        d2 = end
                    else:
                        print unicode(s), d1, d2, 'aanwezig'
                        print unicode(s), d2, start, 'ontbreekt'
                        d1 = start
                        d2 = end
            if empty:
                print unicode(s), first, last, 'ontbreekt'
            else:
                if d1 != start:
                    print unicode(s), d1, d2, 'aanwezig'
                if d2 < last:
                    print unicode(s), d2, last, 'ontbreekt' 
                