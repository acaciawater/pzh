'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.data.models import Project, Parameter

from acacia.data.knmi.models import Station
from acacia.data.models import Datasource, Generator
from acacia.meetnet.models import Well
from django.contrib.auth.models import User

import math
from openpyxl.chart import series
def distance(obj, pnt):
    dx = obj.location.x - pnt.x
    dy = obj.location.y - pnt.y
    return math.sqrt(dx*dx+dy*dy)

def closest_object(query,target):
    closest = None
    dist = 1e99
    for obj in query:
        d = distance(obj, target)
        if d < dist:
            closest = obj
            dist = d
    return closest

def sort_objects(query,target):
    objs = []
    for obj in query:
        obj.distance = distance(obj, target)
        objs.append(obj)
    return sorted(objs, key=lambda x: x.distance)

def luchtdruk(loc,user):
    ''' Luchtdruk stations toevoegen aan project '''
    
    project = loc.project
    p = loc.location
    generator = Generator.objects.get(name='KNMI uurwaarden')
    me = User.objects.get(username='theo')

    stns = sort_objects(Station.objects.all(),p)
    stn = stns[0] # closest
    name='Meteostation %s ' % stn.naam
    ploc, created = project.projectlocatie_set.get_or_create(name=name,defaults={'location':stn.location})
    mloc, created = ploc.meetlocatie_set.get_or_create(name=name,defaults={'location':stn.location})
    ds, created = Datasource.objects.get_or_create(name=name,generator=generator, defaults = {
        'meetlocatie': mloc,
        'timezone': 'UTC',
        'user': me,
        })
    if created:
        print name
        gen = ds.get_generator_instance()
        ds.url = gen.url + '?stns=%d&start=2013010101' % stn.nummer
        ds.save()
        ds.download()
        ds.update_parameters()
 
    # create timeseries for air pressure
    try:
        pressure = ds.parameter_set.get(name='P')
        series,created = pressure.series_set.get_or_create(name = pressure.name, description = pressure.description, unit = pressure.unit, user = ds.user)
        if created:
            series.replace()
            print series, 'created'
    except Parameter.DoesNotExist:
        print 'Parameter P not found in datasource', ds.name
        # no pressure found in knmi file??
        pass
        
    # set air pressure series for well at current project location
    # update logger installations for all screens at current location
    try:
        for w in loc.well_set.all():
            if w.baro != series:
                w.baro = series
                w.save()
            for s in w.screen_set.all():
                for logpos in s.loggerpos_set.all():
                    if logpos.baro != series:
                        logpos.baro = series
                        logpos.save()
                        print logpos, logpos.start_date, 'updated'
    except Well.DoesNotExist:
        print 'Well not found:', loc.name
        pass
    
class Command(BaseCommand):
    args = ''
    help = 'KNMI luchtdruk stations toevoegen aan project'
        
    def handle(self, *args, **options):
        for project in Project.objects.all():
            user = User.objects.get(username='theo')
            for pl in project.projectlocatie_set.all():
                luchtdruk(pl,user)