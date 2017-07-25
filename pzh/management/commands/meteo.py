'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.data.models import Project, Parameter

from acacia.data.knmi.models import Station
from acacia.data.models import Datasource, Generator
from acacia.meetnet.models import Well, MeteoData
from django.contrib.auth.models import User

def luchtdruk(loc,user):
    ''' Luchtdruk stations toevoegen aan project '''
    
    project = loc.project
    p = loc.location
    generator = Generator.objects.get(classname__icontains='KNMI.uur')
    me = User.objects.get(username='theo')

    stn = Station.closest(p)
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
            if not hasattr(w,'meteo'):
                MeteoData.objects.create(well=w,baro=series)
            else:
                w.meteo.baro = series
                w.save()
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