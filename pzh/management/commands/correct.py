from django.core.management.base import BaseCommand
from acacia.meetnet.models import Screen
from acacia.meetnet.util import drift_correct_screen, recomp
from django.contrib.auth.models import User
from acacia.data.models import Series

class Command(BaseCommand):
    help = 'Correct for drift and bias'
    def add_arguments(self, parser):

        parser.add_argument('-r', '--recreate',
                action='store_true',
                default=False,
                dest = 'recreate',
                help = 'recreate time series before correction')

        parser.add_argument('-s', '--screen',
                action='store',
                dest = 'screen',
                help = 'screen id')

        parser.add_argument('-w', '--well',
                action='store',
                dest = 'well',
                help = 'well id')

        parser.add_argument('-f', '--file',
                action='store',
                dest = 'fname',
                help = 'name of file with well names')
        
    def handle(self, *args, **options):
        
        user = User.objects.filter(is_superuser=True).first()
        print('user=%s' % user.username)
        
        pk = options.get('screen')
        if pk:
            queryset = Screen.objects.get(pk=pk)
        else:
            fname = options.get('fname')
            if fname:
                # read well names from file
                with open(fname,'r') as f:
                    names = [name.strip() for name in f.readlines()]
                    queryset = Screen.objects.filter(well__nitg__in=names)
            else:
                pk = options.get('well')
                if pk:
                    # filter on well
                    queryset = Screen.objects.filter(well=pk)
                else:
                    queryset = Screen.objects.all()
                    
        count = queryset.count()
        recreate = options.get('recreate')
        for index, screen in enumerate(queryset):
            print('%d/%d %s' % (index+1, count, screen))
            if recreate:
                series = screen.find_series()
                if not series:
                    name = '%s COMP' % unicode(screen)
                    series, _created = Series.objects.update_or_create(name=name,defaults={
                        'user': user, 'mlocatie': screen.mloc, 'timezone': 'Etc/GMT-1'
                    })
                recomp(screen, series)
                series.validate(reset=True, accept=True, user=user)
            drift_correct_screen(screen,user)
            
