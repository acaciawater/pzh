'''
Created on Dec 6, 2014

@author: theo
'''
import csv, datetime
from optparse import make_option
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Well,Screen
import pytz
from django.core.exceptions import ObjectDoesNotExist

def extend():
    """ 
    kabellengte info verlengen  
    """
    for screen in Screen.objects.all():
        try:
            prev = screen.loggerpos_set.filter(depth__isnull=False).earliest('start_date')
        except ObjectDoesNotExist:
            continue
        if prev:
            for lp in screen.loggerpos_set.order_by('start_date'):
                if not lp.depth:
                    print 'Extend', lp
                    lp.depth = prev
                    lp.save()
                prev = lp.depth
    
class Command(BaseCommand):
    args = ''
    help = 'Importeer kabellengtes'
    option_list = BaseCommand.option_list + (
            make_option('--file',
                action='store',
                type = 'string',
                dest = 'fname',
                default = '/media/sf_C_DRIVE/Users/theo/Documents/projdirs/Zuid-Holland/validatie20132016/data/Kabellengten1.csv'),
        )
        
    def handle(self, *args, **options):
        fname = options.get('fname')
        CET=pytz.timezone('CET')
        if fname:
            with open(fname,'r') as f:
                reader = csv.DictReader(f, delimiter=',')
                for row in reader:
                    NITG = row['nitg']
                    try:
                        well = Well.objects.get(nitg=NITG)
                        filt = int(row['filter'])
                        screen = well.screen_set.get(nr=filt)
                        datumtijd = '%s %s' % (row['datum'], row['wintertijd'])
                        depth = row.get('kabellengte')
                        if len(depth) > 0:
                            depth = float(depth)
                        else:
                            depth = 0
                        date = datetime.datetime.strptime(datumtijd,'%d/%m/%Y %H:%M')
                        date = CET.localize(date)
                        date = date.date()
                        found = False
                        may2013 = datetime.date(2013,5,1)
                        for lp in screen.loggerpos_set.all():
                            start = lp.start_date.date()
                            end = lp.end_date.date()
                            #if (abs(start - date).days < 2) or (date < may2013 and start < may2013):
                            if (date >= start and date <= end):  
                                found = True
                                print NITG, filt, datumtijd, depth, lp.logger, start
                                lp.depth = depth
                                lp.save()
                        if not found:
                            print 'NOT FOUND:', NITG, filt,datumtijd, depth
                    except Well.DoesNotExist:
                        print 'Well %s not found' % NITG
                    except Screen.DoesNotExist:
                        print 'Screen %s/%03d not found' % (NITG, filt)
        extend()
                        