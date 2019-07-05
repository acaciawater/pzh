'''
Created on Jul 5, 2019

@author: theo
'''
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
    help = 'overzicht metadata'
                        
    def handle(self, *args, **options):
        print 'name, nitg, filter, code, x, y, maaiveld, ahn3, bovenkantbuis, top, bottom, logger, ophangpunt, kabellengte'
        for w in Well.objects.all():
            baro = w.meteo.baro if hasattr(w,'meteo') else None
            for s in w.screen_set.all():
                for lp in s.loggerpos_set.all():
                    print ','.join([str(x) for x in [w.name, w.nitg, s.nr, unicode(s), w.location.x, w.location.y, w.maaiveld, w.ahn, s.refpnt, s.top, s.bottom, lp.logger, lp.refpnt, lp.depth]])
