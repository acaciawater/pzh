'''
Created on Sep 27, 2017

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.data.models import Series, ManualSeries
import pandas as pd
from acacia.meetnet.models import Screen

class Command(BaseCommand):
    args = ''
    help = 'consistentie test'

    def handle(self, *args, **options):
        with open('consist.csv','w') as csv:
            csv.write('filter,boven_maaiveld,boven_buis,onder_filter,voor_installatie,na_installatie\n')
            for screen in Screen.objects.all():
                mv = screen.well.maaiveld
                bkb = screen.refpnt
                bottom = mv-screen.bottom
                data = screen.get_compensated_series()
                artesian = data[data>mv].size
                above = data[data>bkb].size
                below = data[data<bottom].size
                before = 0
                after = 0
                for lp in screen.loggerpos_set.all():
                    before += lp.monfile_set.filter(start_date__lt=lp.start_date).count()
                    after += lp.monfile_set.filter(end_date__gt=lp.end_date).count()
                txt = '{},{},{},{},{},{}'.format(screen,artesian,above,below,before,after)
                print txt
                csv.write(txt+'\n')