'''
Created on Jul 20, 2017

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Screen
import datetime
from acacia.mqtt.models import start

class Command(BaseCommand):
    args = ''
    help = 'maak timeline van metingen'
                        
    def handle(self, *args, **options):
        first = datetime.date(2013,1,1)
        last = datetime.date(2016,12,31)
        for s in Screen.objects.order_by('well','nr'):
            query = s.loggerpos_set.order_by('start_date')
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
            if not empty:
                if d1 != start:
                    print unicode(s), d1, d2, 'aanwezig'
                if d2 < last:
                    print unicode(s), d2, last, 'ontbreekt' 
                