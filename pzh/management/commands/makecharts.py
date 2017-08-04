'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Well
from acacia.meetnet.util import chart_for_well
from datetime import datetime
import os
import pytz
from acacia.data.util import slugify

class Command(BaseCommand):
    help = 'maak grafiekjes'
    def add_arguments(self, parser):
        parser.add_argument('-d', '--dest',
                action='store',
                dest = 'dest',
                default = '.',
                help = 'destination folder')
                        
    def handle(self, *args, **options):
        folder = options.get('dest')
        tz = pytz.timezone('CET')
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
            