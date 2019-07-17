from django.core.management.base import BaseCommand
import logging
from acacia.meetnet.models import Well
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'check data for QC3'

    def handle(self, *args, **options):
        with open('QC3-comp.csv','w') as csv:
            csv.write('screen,points,3b-filter,3d-vol,3e-overloop\n')
            for well in Well.objects.all():
                for screen in well.screen_set.all():
                    try:
                        logger.info(unicode(screen))
                        level = screen.get_compensated_series()
                        zmaaiveld = screen.well.maaiveld
                        ztopbuis = screen.refpnt
                        zbottomfilter = screen.refpnt - screen.bottom
                        qc3b = level[level < zbottomfilter].count()
                        qc3d = level[level > zmaaiveld].count()
                        qc3e = level[level > ztopbuis].count()
                         
                        txt = ','.join(map(str,[screen,level.count(), qc3b, qc3d, qc3e]))
                        logger.info(txt)
                        csv.write('{}\n'.format(txt))
                    except:
                        pass
                