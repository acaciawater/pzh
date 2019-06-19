'''
Created on Dec 6, 2014

@author: theo
'''
import csv, datetime

from django.contrib.auth.models import User
from django.core.management.base import BaseCommand
from django.db.models import Q
import pytz

from acacia.data.models import ProjectLocatie, MeetLocatie, ManualSeries
from acacia.meetnet.models import Well, Screen
from django.conf import settings

class Command(BaseCommand):
    args = ''
    help = 'Importeer handpeilingen en corrigeer voor eerdere tijdzone fouten'
    def add_arguments(self, parser):
        parser.add_argument('-f','--file',
                action='store',
                dest = 'fname',
                default = None,
                help='CSV file met handpeilingen'
        )
        
    def handle(self, *args, **options):
        fname = options.get('fname')
        CET=pytz.timezone('Etc/GMT-1')
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
                        #ploc = ProjectLocatie.objects.get(name=well.nitg)
                        ploc = ProjectLocatie.objects.get(name__in=[well.nitg, well.name])
                        #name1= '%s/%03d' % (well.name, filt)
                        name2= '%s/%03d' % (well.nitg, filt)
                        mloc = ploc.meetlocatie_set.get(name=name2)
                        datumtijd = '%s %s' % (row['Datum'], row['Tijd'])
                        depth = row['Meting']
                        if depth:
                            depth = float(depth)
                        else:
                            continue
                        if not screen.refpnt:
                            print 'Reference point for screen %s not available' % screen
                            continue
                        nap = screen.refpnt - depth
                        date = datetime.datetime.strptime(datumtijd,'%d/%m/%Y %H:%M')
                        date = CET.localize(date)
                        series_name = '%s HAND' % mloc.name
                        series,created = ManualSeries.objects.get_or_create(name=series_name,mlocatie=mloc,defaults={'description':'Handpeiling', 'timezone':'Etc/GMT-1', 'unit':'m NAP', 'type':'scatter', 'user':user})
                        if not created:
                            try:
                                usetz = settings.USE_TZ
                                settings.USE_TZ=False #hack for date filtering
                                sameday = series.datapoints.filter(date__date=date.date())
                                if sameday:
                                    sameday.delete()
                            finally:
                                settings.USE_TZ=usetz
                        if row.get('Verwijderen','nee') == 'nee':
                            pt = series.datapoints.create(date=date,value=nap)
                            print screen, pt.date, pt.value
                    except Well.DoesNotExist:
                        print 'Well %s not found' % NITG
                    except Screen.DoesNotExist:
                        print 'Screen %s/%03d not found' % (NITG, filt)
                    except MeetLocatie.DoesNotExist:
                        print 'Meetlocatie %s/%03d not found' % (NITG, filt)
                    except Exception as e:
                        print e, NITG
                        