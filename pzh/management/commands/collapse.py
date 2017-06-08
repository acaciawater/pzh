'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Datalogger

class Command(BaseCommand):
    args = ''
    help = 'Collapse loggerpos instances'
        
    def handle(self, *args, **options):
        for logger in Datalogger.objects.all():
            posquery = logger.loggerpos_set.order_by('screen').order_by('start_date')
            poslist = list(posquery)
            p1 = None
            for p in poslist:
                print p, p.start_date.date(), p.end_date.date(), p.refpnt, p.depth,
                if p1 is None:
                    p1 = p
                else:
                    p2 = p
                    if p.screen == p1.screen and p.refpnt == p1.refpnt and p.depth == p1.depth and p.start_date.date() <= p1.end_date.date():
                        if p.end_date > p1.end_date:
                            p1.end_date = p.end_date
                            p1.save()
                        # associate monfiles with new loggerpos instance
                        for m in p.monfile_set.all():
                            m.source = p1
                            m.save()
                        p.delete()
                        print 'Deleted'
                        continue
                    else:
                        p1 = p2
                print 'Kept'
                continue
