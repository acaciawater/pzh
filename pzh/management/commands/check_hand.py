from django.core.management.base import BaseCommand

from acacia.data.models import ManualSeries, DataPoint
from acacia.meetnet.models import Screen
from datetime import timedelta

class Command(BaseCommand):
    args = ''
    help = 'Check afwijkende handpeilingen'

    def find_nearest(self, queryset, date):
        points = queryset.order_by('date')
        d1 = None
        d2 = None
        
        p1 = points.filter(date__lte=date).last()
        p2 = points.filter(date__gte=date).first()
        if p1 and p2:
            d1 = date - p1.date
            d2 = p2.date - date
            if d1 < d2:
                return p1
            elif d2 < d1:
                return p2
            else:
                # same distance from date: return average
                return DataPoint(date=date,value=(p1.value+p2.value)/2.0)
        elif p1:
            return p1
        elif p2:
            return p2
        else:
            return None
                
    def process(self, peilingen, series, date, tolerance):
        levels = series.datapoints.filter(date__range=(date-tolerance, date+tolerance))
        level = self.find_nearest(levels, date) if levels else None
        points = peilingen.datapoints.filter(date__range=(date-tolerance, date+tolerance))
        peiling = self.find_nearest(points, date) if points else None 
        return (peiling,level) 

    def _toString(self,dp):
        return ','.join(map(str,[dp.date, dp.value])) if dp else ','

    def toString(self,dp):
        return ','.join([self._toString(p) for p in dp])

    def handle(self, *args, **options):
        tolerance = timedelta(hours=2)
        print 'screen,hand.date,hand.value,logger.date,logger.value'
        for screen in Screen.objects.all():
            series = screen.find_series()
            peilingen = screen.mloc.series_set.instance_of(ManualSeries).filter(name__endswith='HAND').first()
            if peilingen:
                for mon in screen.get_monfiles():
                    start=self.process(peilingen, series, mon.start_date, tolerance)
                    stop=self.process(peilingen, series, mon.end_date, tolerance)
                    print ','.join([mon.name,self.toString(start)])
                    print ','.join([mon.name,self.toString(stop)])
                    