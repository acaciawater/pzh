'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Well
from acacia.meetnet.util import chart_for_well, chart_for_screen
import os
from acacia.data.util import slugify
import pytz
import datetime
from django.shortcuts import get_object_or_404

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

        parser.add_argument('-w', '--well',
                action='store',
                dest = 'well',
                default = False,
                help = 'id of well to make charts for')

        parser.add_argument('-b', '--begin',
                action='store',
                dest = 'begin',
                default = None,
                help = 'first year')

        parser.add_argument('-e', '--end',
                action='store',
                dest = 'end',
                default = None,
                help = 'last year')

        parser.add_argument('-o', '--overwrite',
                action='store_true',
                dest = 'overwrite',
                default = False,
                help = 'overwrite existing charts')

        parser.add_argument('-r', '--raw',
                action='store_true',
                dest = 'raw',
                default = False,
                help = 'include raw data')
        
        parser.add_argument('-c', '--corrected',
                action='store_true',
                dest = 'corrected',
                default = False,
                help = 'include corrected data')

        parser.add_argument('-f', '--file',
                action='store',
                dest = 'fname',
                default = None,
                help = 'name of file with well names')
        
                        
    def handle(self, *args, **options):
        folder = options.get('dest')
        overwrite = options.get('overwrite')
        noscreen = options.get('noscreen')
        begin = options.get('begin')
        end = options.get('end')
        tz = pytz.timezone('CET')
        pk = options.get('well')
        fname = options.get('fname')
        raw = options.get('raw')
        corrected = options.get('corrected')
        if not raw and not corrected:
            # include at least something..
            raw = True

        start=datetime.datetime(int(begin),1,1,tzinfo=tz) if begin else None
        stop=datetime.datetime(int(end),12,31,tzinfo=tz) if end else None
        if not os.path.exists(folder):
            os.makedirs(folder)
        if fname:
            with open(fname,'r') as f:
                names = [name.strip() for name in f.readlines()]
                queryset = Well.objects.filter(nitg__in=names)
        else:
            queryset = [get_object_or_404(Well,pk=pk)] if pk else Well.objects.all()
        for w in queryset:
            filename = os.path.join(folder,slugify(unicode(w)) + '.png')
            if overwrite or not os.path.exists(filename):
                print filename
                data = chart_for_well(w,start=start,stop=stop,corrected=corrected)
                with open(filename,'wb') as png:
                    png.write(data)
            if not noscreen:
                for s in w.screen_set.all():
                    filename = os.path.join(folder,slugify(unicode(s)) + '.png')
                    if overwrite or not os.path.exists(filename):
                        print filename
                        data = chart_for_screen(s,start=start,stop=stop,raw=raw,corrected=corrected)
                        with open(filename,'wb') as png:
                            png.write(data)
