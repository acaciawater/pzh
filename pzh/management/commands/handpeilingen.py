'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Screen
from acacia.data.models import ManualSeries

class Command(BaseCommand):
    args = ''
    help = 'aantal handpeilingen per filter'
                        
    def handle(self, *args, **options):
        print 'name, nitg, filter, code, handpeilingen'
        for series in ManualSeries.objects.order_by('name'):
            aantal = series.aantal() if series else 0
            if aantal:
                mloc = series.meetlocatie()
                s = mloc.screen_set.first()
                if s is None:
<<<<<<< HEAD
                    print '#'+str(series), 'has no screen attached.'
=======
                    print '#'+s, 'has no screen attached'
>>>>>>> branch 'pzh2017' of https://github.com/acaciawater/pzh
                else:
                    print ','.join([str(x) for x in [s.well.name, s.well.nitg, s.nr, unicode(s), aantal]])
#         for s in Screen.objects.order_by('well__name', 'nr'):
#             series = s.mloc.series_set.filter(name__endswith='HAND').first()
#             aantal = series.aantal() if series else 0
#             if aantal:
#                 print ','.join([str(x) for x in [s.well.name, s.well.nitg, s.nr, unicode(s), aantal]])
