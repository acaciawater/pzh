'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Well, Datalogger


def q(x):
    return '"{}"'.format(x)

def d(x):
    return x.strftime('%d-%m-%Y %H:%M')

class Command(BaseCommand):
    args = ''
    help = 'overzicht loggers naar leeftijd'
                        
    def handle(self, *args, **options):
        print 'screen,logger,start,stop,days,replacement,date'
        for logger in Datalogger.objects.all():
            if logger.loggerpos_set.exists():
                install = logger.loggerpos_set.order_by('start_date')
                first = install.first() 
                last = install.last()
                start_date = first.start_date
                end_date = last.end_date or last.start_date
                duration = end_date - start_date
                # check if other logger has been installed in screen (this one has been replaced)
                more = last.screen.loggerpos_set.exclude(logger__serial=logger.serial).filter(start_date__gt=start_date).order_by('start_date')
                if more.exists():
                    next = more.first()
                    replacement = next.logger.serial
                    date = next.start_date
                    status = 'replaced'
                else:
                    replacement = None
                    date = end_date
                    status = 'last seen'
                print '{},{},{:%Y-%m-%d},{:%Y-%m-%d},{},{},{:%Y-%m-%d}'.format(last.screen, logger, start_date, end_date, duration.days, replacement, date)
