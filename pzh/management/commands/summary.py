'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.meetnet.models import LoggerPos, Well
from time import strftime

def q(x):
    return '"{}"'.format(x)

def d(x):
    return x.strftime('%d-%m-%Y %H:%M')

class Command(BaseCommand):
    args = ''
    help = 'overzicht loggers en files'
                        
    def handle(self, *args, **options):
        print 'name, nitg, filter, refpnt, top, bottom, logger, start, end, refpnt, depth, baro, monserial, file, monstart, monend, num_points'
        for w in Well.objects.all():
            for s in w.screen_set.all():
                for lp in s.loggerpos_set.all():
                    for mf in lp.monfile_set.all():
                        print ','.join([str(x) for x in [w.name, w.nitg, s.nr, s.refpnt, s.top, s.bottom, lp.logger, d(lp.start_date), d(lp.end_date), lp.refpnt, lp.depth, q(lp.baro), mf.serial_number, q(mf.name), d(mf.start_date), d(mf.end_date), mf.num_points]])
                    