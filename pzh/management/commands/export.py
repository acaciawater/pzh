import os

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from acacia.meetnet.models import Screen

class Command(BaseCommand):
    args = ''
    help = 'Export series'
    
    def add_arguments(self, parser):
        parser.add_argument('--screens', '-s', dest = 'screens', help = 'File with screen names to export')
    
    fldr = './export'

    def dump(self, series, name):
        name = slugify(name)
        fname = os.path.join(self.fldr,name) + '.csv'
        print fname
#         with open(fname,'w') as f:
#             text = series.to_csv()
#             f.write(text)
        
    def handle(self, *args, **options):
        if not os.path.exists(self.fldr):
            os.makedirs(self.fldr)
        screen_file = options['screens']
        with open(screen_file,'rt') as f:
            screens = [line.strip() for line in f]
        for screen in Screen.objects.all():
            name = '%s/%03d' % (screen.well.nitg, screen.nr)
            if not screen_file or name in screens:
                comp = screen.find_series()
                if comp:
                    self.dump(comp, slugify('%s-comp' % name))

                corr = screen.mloc.series_set.filter(name__iendswith='corr').first()
                if corr:
                    self.dump(corr, slugify('%s-corr' % name))
                    
                hand = screen.mloc.series_set.filter(name__iendswith='hand').first()
                if hand:
                    self.dump(corr, slugify('%s-hand' % name))
                    
