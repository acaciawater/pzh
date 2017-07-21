'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Well


def q(x):
    return '"{}"'.format(x)

def d(x):
    return x.strftime('%d-%m-%Y %H:%M')

class Command(BaseCommand):
    args = ''
    help = 'overzicht loggers en files'
                        
    def handle(self, *args, **options):
        print 'name, nitg, filter, code, refpnt, top, bottom, logger, refpnt, depth, baro, file, begin, end, days, points'
        for w in Well.objects.all():
            for s in w.screen_set.all():
                for lp in s.loggerpos_set.all():
                    for mf in lp.monfile_set.all():
                        print ','.join([str(x) for x in [w.name, w.nitg, s.nr, unicode(s), s.refpnt, s.top, s.bottom, lp.logger, lp.refpnt, lp.depth, q(lp.baro), q(mf.name), d(mf.start_date), d(mf.end_date), (mf.end_date-mf.start_date).days, mf.num_points]])
                    