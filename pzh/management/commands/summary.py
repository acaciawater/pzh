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
        print 'name, nitg, filter, code, maaiveld, ahn3, bovenkantbuis, top, bottom, logger, ophangpunt, kabellengte, baro, aantal, monfile, monbegin, moneinde, monaantal'
        for w in Well.objects.all():
            baro = w.meteo.baro if hasattr(w,'meteo') else None
            for s in w.screen_set.all():
                series = s.mloc.series_set.filter(name__endswith='COMP').first()
                for lp in s.loggerpos_set.all():
                    #lppts = series.datapoints.filter(date__gte=lp.start, date__lte=lp.stop).count() if series else 0
                    for mf in lp.monfile_set.all():
                        mfpts = series.datapoints.filter(date__gte=mf.start_date, date__lte=mf.end_date).count() if series else 0
                        print ','.join([str(x) for x in [w.name, w.nitg, s.nr, unicode(s), w.maaiveld, w.ahn, s.refpnt, s.top, s.bottom, lp.logger, lp.refpnt, lp.depth, q(baro), mfpts, q(mf.name), d(mf.start_date), d(mf.end_date), mf.num_points]])
