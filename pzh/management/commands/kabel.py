'''
Created on Dec 6, 2014

@author: theo
'''
import csv, datetime
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Well,Screen
import pytz
from datetime import timedelta

class Command(BaseCommand):
    args = ''
    help = 'Importeer kabellengtes'

    def add_arguments(self, parser):
        parser.add_argument('-f','--file',
                action='store',
                dest = 'fname',
                default = None,
                help='CSV file with cable lengths'
        )
        
    def handle(self, *args, **options):
        fname = options.get('fname')
        CET=pytz.timezone('Etc/GMT-1')
        if fname:
            with open(fname,'r') as f:
                reader = csv.DictReader(f, delimiter=',')
                for row in reader:
                    NITG = row['nitg']
                    try:
                        well = Well.objects.get(nitg=NITG)
                        filt = int(row['filter'])
                        screen = well.screen_set.get(nr=filt)
                        datumtijd = '%s %s' % (row['datum'], row['tijd'])
                        depth = row.get('kabellengte')
                        if len(depth) > 0:
                            depth = float(depth)
                        else:
                            depth = 0
                        timestamp = datetime.datetime.strptime(datumtijd,'%d/%m/%Y %H:%M')
                        timestamp = CET.localize(timestamp)

                        # date lookups on start_date dont not work with MySQL, so use datetime lookups
                        date1 = timestamp.replace(hour=0,minute=0,second=0)
                        date2 = date1+timedelta(days=1)
                        
                        if timestamp.year < 2013:
                            q = screen.loggerpos_set.filter(start_date__year__lte=2013)
                        else:
                            # filter on start_date__date = timestamp.date
                            q = screen.loggerpos_set.filter(start_date__range=[date1,date2])
                        if q:
                            q.update(depth=depth)
                        else:
                            print 'NOT FOUND:', NITG, filt,datumtijd, depth
                            
                            # find installation with start_date < timestamp and end_date > timestamp
                            q = screen.loggerpos_set.filter(start_date__lte=timestamp, end_date__gte=timestamp)
                            if q:
                                if q.count() != 1:
                                    print('Cannot split loggerpos. Installation not unique')
                                lp = q.first()
                                lp1 = screen.loggerpos_set.create(
                                    logger=lp.logger,
                                    start_date = lp.start_date,
                                    end_date = timestamp,
                                    refpnt = lp.refpnt,
                                    depth = lp.depth)
                                lp2 = screen.loggerpos_set.create(
                                    logger=lp.logger,
                                    start_date = timestamp,
                                    end_date = lp.end_date,
                                    refpnt = lp.refpnt,
                                    depth = depth)
                                # move all monfiles from lp to lp1
                                mon1 = lp.monfile_set.all()
                                mon1.update(source=lp1)
                                # move mon files that start on or after date of timestamp to lp2
                                mon2 = lp1.monfile_set.filter(start_date__gte=date1)
                                mon2.update(source=lp2)
                                print 'Splitted;', lp
                                lp.delete()
                            else:
                                print 'No matching logger installation found'
#                         found = False
#                         for lp in screen.loggerpos_set.all():
#                             start = lp.start_date.date()
#                             if (abs(start - date).days < 2) or (date.year < 2013 and start.year < 2013):
#                                 found = True
#                                 print NITG, filt,datumtijd, depth
#                                 lp.depth = depth
#                                 lp.save()
#                         if not found:
#                             print 'NOT FOUND:', NITG, filt,datumtijd, depth
                    except Well.DoesNotExist:
                        print 'Well %s not found' % NITG
                    except Screen.DoesNotExist:
                        print 'Screen %s/%03d not found' % (NITG, filt)
                        