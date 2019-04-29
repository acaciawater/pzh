'''
Created on Apr 26, 2019

@author: theo
'''

from django.core.management.base import BaseCommand
from acacia.meetnet.models import Screen, MonFile
import pytz

class Command(BaseCommand):
    args = ''
    help = 'check for overlapping mon files'
        
    def handle(self, *args, **options):
        CET=pytz.timezone('Etc/GMT-1')
        print 'well,screen,monfile,diver,start_date,start_time,stop_date,stop_time,count,overlap'
        for screen in Screen.objects.all():
            files = MonFile.objects.filter(datasource__meetlocatie=screen.mloc)
            for mon in files.order_by('start_date'):
                others = files.exclude(pk=mon.pk)
                overlap = others.filter(start_date__lt=mon.end_date, end_date__gt=mon.start_date)
                start = mon.start_date.astimezone(CET)
                stop = mon.end_date.astimezone(CET)
                print ','.join(map(str,[screen.well.nitg, screen.nr, mon.filename(), mon.serial_number, start.date(), start.time(), stop.date(), stop.time(), mon.num_points, overlap.count()]))
                