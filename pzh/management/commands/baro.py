'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.meetnet.models import LoggerPos

class Command(BaseCommand):
    args = ''
    help = 'Default baro reeksen toekennen aan putten adhv logger installaties'
                        
    def handle(self, *args, **options):
        for lp in LoggerPos.objects.all():
            well = lp.screen.well
            if well.baro is None:
                well.baro = lp.baro
                well.save()
                