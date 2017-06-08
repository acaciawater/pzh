'''
Created on May 21, 2017

@author: theo
'''
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import Point
import pandas as pd
import datetime
from acacia.meetnet.models import Network, Well
from acacia.data.models import Project
from acacia.data.util import RDNEW
import numpy
from math import isnan
 
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
    help = 'Imports metadata of wells and screens'
    
    def add_arguments(self, parser):
        parser.add_argument(dest='filename',
                help='Name of Excel file')

    def import_putten(self,filename,sheetname):
        df = pd.read_excel(filename,sheetname=sheetname,index_col=0)
        net = Network.objects.first()
        prj = Project.objects.first()
        for index,row in df.iterrows():
            x = asfloat(row['X-Coordinaat'])
            y = asfloat(row['Y-Coordinaat'])
            loc = Point(x,y,srid=RDNEW)
            nitg = row['NITG-code']
            name = row['OLGA nummer']
            #print '{}="{}"'.format(nitg,name)
            if str(name)=='nan' or name is None or name=='': 
                name = nitg 
            try:
                ploc, created = prj.projectlocatie_set.get_or_create(name=name,defaults={'location':loc})
                well, created = ploc.well_set.get_or_create(name=name,nitg=nitg,defaults={
                    'network': net,
                    'location':loc,
                    'maaiveld':float(row['Mv-hoogte']),
                    'description':row['Locatie'],
                    'date':datetime.datetime(1980,1,1)
                    })
                if created:
                    print unicode(well) 
            except Exception as e:
                print nitg,e

    def import_filters(self,filename,sheetname):
        df = pd.read_excel(filename,sheetname=sheetname)
        net = Network.objects.first()
        prj = Project.objects.first()
        for index,row in df.iterrows():
            put = row['Put']
            try:
                well = Well.objects.get(nitg=put)
            except Well.DoesNotExist:
                print 'well {} does not exist'.format(put)
                continue
            
            nr = row['Filternummer']
            top = asfloat(row['Filter van'])
            bot = asfloat(row['Filter tot'])
            ref = asfloat(row['Bovenkant [m NAP]'])
            dia = asfloat(row['Diameter [mm]'])
            
            #print '{}.{:03d}'.format(put,nr)
             
            screen, created = well.screen_set.get_or_create(nr=nr,defaults = {
                'refpnt': ref,
                'top': top,
                'bottom': bot,
                'diameter': dia})
            if created:
                print unicode(screen)
            screen.mloc, _ = well.ploc.meetlocatie_set.get_or_create(name=unicode(screen),defaults = {
                'location': well.ploc.location})
            if created:
                screen.save()
                    
    def handle(self, *args, **options):
        filename = options['filename']
        self.import_putten(filename,'Putgegevens')
        self.import_filters(filename,'Filtergegevens')
