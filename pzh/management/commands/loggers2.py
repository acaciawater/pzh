'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Datalogger, Screen, LoggerPos
from django.db.models.aggregates import Count, Min, Max
from datetime import datetime
import pytz


def q(x):
    return '"{}"'.format(x)

def d(x):
    return x.strftime('%d-%m-%Y %H:%M')

class Command(BaseCommand):
    args = ''
    help = 'overzicht logger installatie per filter'
                        
    def handle(self, *args, **options):
        print 'screen,logger,start,stop,days'
        jan2018 = pytz.utc.localize(datetime(2018,1,1))
        
        for screen in Screen.objects.order_by('well__nitg','nr'):
            print screen,
            try:
                current = screen.loggerpos_set.latest('start_date')
            except:
                # no logger installed
                print ',,,,'
                continue
#             if current is None or current.end_date < jan2018:
#                 print ',,,,'
#                 continue 
            # get age of current logger
            span = current.logger.loggerpos_set.aggregate(start=Min('start_date'),stop=Max('end_date'))
            start = span['start']
            stop = span['stop'] or jan2018 
            age = stop-start
            print ',{},{:%Y-%m-%d},{:%Y-%m-%d},{}'.format(current.logger, start, stop, age.days)

    def handle1(self, *args, **options):
        print 'screen,logger,start,stop,days'
        for logger in Datalogger.objects.all():
            if logger.loggerpos_set.exists():
                # this logger has been installed in one or more screens
                screens = set(logger.loggerpos_set.values_list('screen',flat=True))
                for screen_id in screens:
                    screen = Screen.objects.get(id=screen_id)
                    install = logger.loggerpos_set.filter(screen=screen).aggregate(start=Min('start_date',distinct=True),stop=Max('end_date',distinct=True))
                    stop = install['stop'] or datetime.datetime(2018,1,1)
                    start = install['start']
                    duration = stop - start
                    print '{},{},{:%Y-%m-%d},{:%Y-%m-%d},{}'.format(screen, logger, start, stop, duration.days)
