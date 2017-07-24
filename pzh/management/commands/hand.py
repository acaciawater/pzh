'''
Created on Dec 6, 2014

@author: theo
'''
import csv, datetime
from django.core.management.base import BaseCommand
from acacia.data.models import MeetLocatie, ManualSeries
from acacia.meetnet.models import Well,Screen
from django.db.models import Q
from django.contrib.auth.models import User
import pytz

class Command(BaseCommand):
    args = ''
    help = 'Importeer handpeilingen'

    def add_arguments(self, parser):
        parser.add_argument(dest='fname',
                help='Name of csv file with water level readings')
        
        
    def handle(self, *args, **options):
        fname = options.get('fname')
        TZ=pytz.timezone('CET') # handpeilingen worden aangeleved in CET
        user=User.objects.get(username='theo')
        if fname:
            with open(fname,'r') as f:
                reader = csv.DictReader(f, delimiter=',')
                for row in reader:
                    NITG = row['NITG']
                    try:
                        well = Well.objects.get(Q(nitg=NITG) | Q(name=NITG))
                        filt = int(row['Filter'])
                        screen = well.screen_set.get(nr=filt)
                        mloc = screen.mloc
                        datumtijd = '%s %s' % (row['Datum'], row['Tijd'])
                        depth = row['Meting']
                        if depth:
                            depth = float(depth)
                        else:
                            depth = 0
                        if not screen.refpnt:
                            print 'Reference point for screen %s not available' % screen
                            continue
                        nap = screen.refpnt - depth
                        date = datetime.datetime.strptime(datumtijd,'%d/%m/%Y %H:%M:%S')
                        date = TZ.localize(date)
                        series_name = '%s HAND' % mloc.name
                        series, created = ManualSeries.objects.get_or_create(name=series_name, mlocatie=mloc, defaults = {'description': 'Handpeiling', 'unit': 'm NAP', 'type': 'scatter', 'user':user})
                        pt, created = series.datapoints.get_or_create(date=date,defaults={'value': nap})
                        if not created:
                            pt.value = nap
                            pt.save()
                        print screen, pt.date, pt.value
                    except Well.DoesNotExist:
                        print 'Well %s not found' % NITG
                    except Screen.DoesNotExist:
                        print 'Screen %s/%03d not found' % (NITG, filt)
                    except MeetLocatie.DoesNotExist:
                        print 'Meetlocatie %s/%03d not found' % (NITG, filt)
                    except Exception as e:
                        print e, NITG
                        