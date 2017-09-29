'''
Created on Jul 31, 2017

@author: theo
'''
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User 
from acacia.meetnet.models import Well
from acacia.meetnet.util import recomp, make_chart
from datetime import datetime
import os
import pytz
from acacia.data.models import Series
from acacia.data.util import slugify

class Command(BaseCommand):
    help = 'timeseries en grafiekjes op nieuw aanmaken'
    def add_arguments(self, parser):
        parser.add_argument('-w', '--well',
                action='store',
                dest = 'pk',
                default = None,
                help = 'primary key of well')
        parser.add_argument('-d', '--dest',
                action='store',
                dest = 'dest',
                default = '.',
                help = 'destination folder for charts')

    def save_chart(self, obj, folder):
        chart = make_chart(obj)
        filename = os.path.join(folder,slugify(unicode(obj)) + '.png')
        print filename
        with open(filename,'wb') as png:
            png.write(chart)
                                
    def handle(self, *args, **options):
        pk = options.get('pk')
        folder = options.get('dest')
        tz = pytz.timezone('CET')
        start=datetime(2013,1,1,tzinfo=tz)
        stop=datetime(2016,12,31,tzinfo=tz)
        user=User.objects.get(username='theo')
        if pk:
            wells = Well.objects.filter(pk=pk)
        else:
            wells = Well.objects.all()
        for w in wells:
            print 'Well', unicode(w)
            for screen in w.screen_set.all():
                name = '%s COMP' % unicode(screen)
                print 'Screen', unicode(screen)
                series, created = Series.objects.get_or_create(name=name,defaults={'mlocatie':screen.mloc,'user':user})
                recomp(screen, series)
                self.save_chart(screen,folder)
            self.save_chart(w,folder)
            