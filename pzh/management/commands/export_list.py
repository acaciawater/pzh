import os

from django.core.management.base import BaseCommand
from django.utils.text import slugify
from acacia.meetnet.models import Screen

class Command(BaseCommand):
    args = ''
    help = 'Export series from screen list'
    
    def add_arguments(self, parser):
        parser.add_argument('file')
    
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
        screen_list = options['file']
        with open(screen_list,'rt') as f:
            screens = [line.strip() for line in f]
        for screen in Screen.objects.all():
            name = '%s/%03d' % (screen.well.nitg, screen.nr)
            if name in screens:
                
                comp = screen.find_series()
                if comp:
                    self.dump(comp, slugify('%s-comp' % name))

                corr = screen.mloc.series_set.filter(name__iendswith='corr').first()
                if corr:
                    self.dump(corr, slugify('%s-corr' % name))
                    
