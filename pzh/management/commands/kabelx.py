'''
Created on Dec 6, 2014

@author: theo
'''
import datetime
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Network, Well, Screen
from acacia.data.models import Project
import pytz
import pandas as pd
import numpy
from math import isnan

BOOK = '/media/sf_C_DRIVE/Users/theo/Documents/projdirs/Zuid-Holland/validatie20132016/data/veldrapportages.xlsx'
SHEET = 'Export'

def asfloat(x):
    try:
        x = float(x)
        if not (isnan(x) or numpy.isnan(x)):
            return x
    except:
        pass
    
    return None

class Command(BaseCommand):

    args = ''
    help = 'Importeer kabellengtes'
            
    def add_arguments(self, parser):
        parser.add_argument(dest='book',
                default=BOOK,
                help='Name of Excel workbook')
        
        parser.add_argument(dest='sheet',
                help='Name of worksheet',
                default=SHEET)

    def handle(self, *args, **options):
        book = options.get('book')
        sheet = options.get('sheet')
        CET=pytz.timezone('CET')
        df = pd.read_excel(book,sheetname=sheet,index_col=0)
        net = Network.objects.first()
        prj = Project.objects.first()
        may2013 = datetime.date(2013,5,1)
        for index,row in df.iterrows():
            try:
                filt = int(row['filter'])
                if filt == 0:
                    continue
                NITG = row['NITG']
                print index, NITG,
                well = Well.objects.get(nitg=NITG)
                screen = well.screen_set.get(nr=filt)
                oud = asfloat(row.get('oude kabel (bkb-membrn m)'))
                new = asfloat(row.get('nieuwe kabel (bkb-membrn m)'))
                depth = new or oud
                if depth is None:
                    print 'No kabel'
                    continue
                datum = row['datum']
                if datum is None or pd.isnull(datum):
                    print 'No date'
                    continue
                date = datum.date()
                found = False
                for lp in screen.loggerpos_set.all():
                    start = lp.start_date.date()
                    if (abs(start - date).days < 2) or (date < may2013 and start < may2013):
                        found = True
                        print filt, date, depth
                        lp.depth = depth
                        lp.save()
                if not found:
                    print 'NOT FOUND:', filt, date, depth
            except Well.DoesNotExist:
                print 'Well %s not found' % NITG
            except Screen.DoesNotExist:
                print 'Screen %s/%03d not found' % (NITG, filt)
                