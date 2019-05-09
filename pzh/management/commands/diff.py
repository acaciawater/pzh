'''
Created on Dec 6, 2014

@author: theo
'''
from django.core.management.base import BaseCommand
from acacia.data.models import Series, ManualSeries
import pandas as pd
from acacia.meetnet.models import Screen

class Command(BaseCommand):
    args = ''
    help = 'Vergelijk standen en handpeilingen'

    def handle(self, *args, **options):

        tolerance = pd.Timedelta('1 hour')
        print 'tolerance:',tolerance
        
        header = True
        with open('diff.csv','w') as csv:
            for screen in Screen.objects.all():
                print unicode(screen),
                hand = screen.get_manual_series()
                if hand is None:
                    print 'geen handpeilingen'
                else:
                    src = screen.get_compensated_series()
                    if src is None:
                        print 'geen loggerdata'
                    else:
                        try:
                            data = src.reindex(hand.index,method='nearest',tolerance=tolerance)
                            verschil = data - hand
                            df = pd.DataFrame({'filter': unicode(screen), 'data': data, 'hand': hand, 'verschil': verschil})
                            df.dropna(inplace=True)
                            print verschil.mean()
                            df.to_csv(csv,header=header)
                            header = False
                        except Exception as e:
                            print 'problem with',screen,e

    def handle2(self, *args, **options):
        with open('diff.csv','w') as csv:
            for screen in Screen.objects.all():
                print unicode(screen),
                hand = screen.get_manual_series()
                if hand is None:
                    print 'geen handpeilingen'
                else:
                    data = screen.get_compensated_series()
                    if data is None:
                        print 'geen loggerdata'
                    else:
                        left,right=data.align(hand)
                        data = left.interpolate(method='time')
                        data = data.reindex(hand.index)
                        verschil = data - hand
                        df = pd.DataFrame({'filter': unicode(screen), 'data': data, 'hand': hand, 'verschil': verschil})
                        df.dropna(inplace=True)
                        print verschil.mean()
                        df.to_csv(csv)
            
    def handle1(self, *args, **options):
        dfall = None
        for h in ManualSeries.objects.all():
            hand = h.to_pandas()
            mloc = h.meetlocatie()
            print mloc
            try:
                name = '%s COMP' % mloc.name
                ser = Series.objects.get(name = name)
                try:
                    if ser.mlocatie != mloc:
                        ser.mlocatie = mloc
                        ser.save()
                except Exception as e:
                    print e
                    continue
            except Series.DoesNotExist:
                print 'Series', name, 'not found' 
                continue
            
            data = ser.to_pandas()

            left,right=data.align(hand)
            data = left.interpolate(method='time')
            data = data.reindex(hand.index)
            verschil = data - hand
            df = pd.DataFrame({'locatie': str(mloc), 'data': data, 'hand': hand, 'verschil': verschil})
            df.dropna(inplace=True)

            if dfall is None:
                dfall = df
            else:
                dfall = dfall.append(df)
            dfall.to_csv('diff.csv')
            