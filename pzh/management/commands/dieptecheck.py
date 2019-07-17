from django.core.management.base import BaseCommand
import os
import logging
import numpy as np
from acacia.meetnet.models import Well
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'check dieptes filters'

    def handle(self, *args, **options):
        for well in Well.objects.all():
            screens = well.screen_set.order_by('nr')
            last = None
            for s in screens:
                if s.depth < 1:
                    logger.warning('{} depth tube less than 1 m'.format(s))
                if s.top < 0:
                    logger.warning('{} top screen above top tube'.format(s))
                if s.top > s.bottom:
                    logger.warning('{} top screen below bottom screen'.format(s))
                elif s.bottom - s.top < 0.5:
                    logger.warning('{} screen length less than 0.5 m'.format(s))
                if s.bottom > s.depth:
                    logger.warning('{} bottom screen below bottom of tube'.format(s))
                if last and last.bottom > s.top:
                        logger.warning('{} top ({}) above bottom of {} ({})'.format(s,s.top,last,last.top))
                last = s
