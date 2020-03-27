import os, re

from django.core.management.base import BaseCommand
from django.db.models import Q

from acacia.meetnet.models import Well, Screen
from acacia.meetnet.util import createmonfile


class Command(BaseCommand):
    args = ''
    help = 'Peek in monfiles and print summary'

    def add_arguments(self, parser):
        parser.add_argument('-a','--all',
                action='store_true',
                dest = 'all',
                default = False,
                help='print all files, also for unknown locations'
        )
        parser.add_argument('-f','--file',
                action='store',
                dest = 'fname',
                default = None,
                help='Monfile'
        )
        parser.add_argument('-d','--dir',
                action='store',
                dest = 'dname',
                default = None,
                help='Directory with monfiles'
        )
        
    def peek(self, fname, all):
        with open(fname) as f:
            mon, channels = createmonfile(f)
            put = mon.location
            match = re.match(r'(\w+)[\.\-](\d{1,3}$)',put)
            if match:
                put = match.group(1)
                filt = int(match.group(2))
            else:
                filt = 1
            try:
                well = Well.objects.get(Q(nitg=put) | Q(name=put))
                wname = well.nitg or well.name
                screen = well.screen_set.get(nr=filt)
                nr = screen.nr
            except Well.DoesNotExist:
                if not all:
                    return
                wname = 'n/a'
                nr = 'n/a'
            except Screen.DoesNotExist:
                if not all:
                    return
                nr = 'n/a'
                
            print('{name},{location},{well},{screen},{logger},{start},{stop},{count}'.
                  format(name=os.path.basename(fname),
                         location=mon.location,
                         well=wname,
                         screen=nr,
                         logger=mon.serial_number,
                         start=mon.start_date,
                         stop=mon.end_date,
                         count=mon.num_points))
            
    def handle(self, *args, **options):
        fname = options.get('fname')
        dname = options.get('dname')
        all = options.get('all')
        print('name,location,well,screen,logger,start,stop,count')
        if dname:
            for path, _dirs, files in os.walk(dname):
                for name in files:
                    if name.lower().endswith('.mon'):
                        self.peek(os.path.join(path,name),all)
        if fname:
            self.peek(fname,all)
