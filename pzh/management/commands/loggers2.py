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
        print 'screen,logger,refpnt,length,start,stop,days'
        mei2019 = pytz.utc.localize(datetime(2019,5,10))
        
        for screen in Screen.objects.order_by('well__nitg','nr'):
            print screen,
            try:
                current = screen.loggerpos_set.latest('start_date')
            except:
                # no logger installed
                print ',,,,,,'
                continue
            # get age of current logger
            span = current.logger.loggerpos_set.aggregate(start=Min('start_date'),stop=Max('end_date'))
            start = span['start']
            stop = span['stop'] or mei2019 
            age = stop-start
            print ',{},{},{},{:%Y-%m-%d},{:%Y-%m-%d},{}'.format(current.logger, current.refpnt, current.depth, start, stop, age.days)

