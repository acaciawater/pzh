import os

from django.core.management.base import BaseCommand
from acacia.data.models import Series
from django.utils.text import slugify

class Command(BaseCommand):
    args = ''
    help = 'Export all series'
        
    fldr = './export'
    
    def handle(self, *args, **options):
        if not os.path.exists(self.fldr):
            os.makedirs(self.fldr)
        for s in Series.objects.all():
            if s.parameter:
                name = unicode(s.parameter)
            else: 
                name = s.name
            name = slugify(name)
            fname = os.path.join(self.fldr,name) + '.csv'
            print fname
            with open(fname,'w') as f:
                text = s.to_csv()
                f.write(text)
