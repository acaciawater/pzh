'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Well
from acacia.meetnet.util import chart_for_well, chart_for_screen
import os
from acacia.data.util import slugify

class Command(BaseCommand):
    help = 'maak grafiekjes'
    def add_arguments(self, parser):
        parser.add_argument('-d', '--dest',
                action='store',
                dest = 'dest',
                default = '.',
                help = 'destination folder')

        parser.add_argument('-s', '--noscreen',
                action='store_true',
                dest = 'noscreen',
                default = False,
                help = 'ignore screens')
                        
    def handle(self, *args, **options):
        folder = options.get('dest')
        noscreen = options.get('noscreen')
        #tz = pytz.timezone('CET')
        #start=datetime(2013,1,1,tzinfo=tz)
        #stop=datetime(2016,12,31,tzinfo=tz)
        if not os.path.exists(folder):
            os.makedirs(folder)
        for w in Well.objects.all():
            data = chart_for_well(w)
            filename = os.path.join(folder,slugify(unicode(w)) + '.png')
            print filename
            with open(filename,'wb') as png:
                png.write(data)
            if not noscreen:
                for s in w.screen_set.all():
                    data = chart_for_screen(s)
                    filename = os.path.join(folder,slugify(unicode(s)) + '.png')
                    print filename
                    with open(filename,'wb') as png:
                        png.write(data)
