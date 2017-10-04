'''
Created on Oct 1, 2017

@author: theo
'''
from django.core.management.base import BaseCommand
import os
import logging
import numpy as np
from acacia.meetnet.models import Well
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'check on raw data below logger depth (dry)'

    def handle(self, *args, **options):
        baros = {}
        with open('dry.csv','w') as csv:
            csv.write('screen,file,from,to,points,dry0,dry2,dry5\n')
            for well in Well.objects.all():
                if not hasattr(well,'meteo') or well.meteo.baro is None:
                    logger.error('No air pressure defined for well {well}'.format(well=well))
                    continue
                baroseries = well.meteo.baro
                logger.info('well {well}, air pressure = {pressure}'.format(well=well,pressure=baroseries.meetlocatie().name))
                if baroseries in baros:
                    baro = baros[baroseries]
                else:
                    baro = baroseries.to_pandas()
            
                    # if baro datasource = KNMI then convert from hPa to cm H2O
                    dsbaro = baroseries.datasource()
                    if dsbaro:
                        gen = dsbaro.generator
                        if 'knmi' in gen.name.lower() or 'knmi' in gen.classname.lower():
                            baro = baro / (well.g or 9.80638)
                    
                    baros[baroseries] = baro

                barostart = baro.index[0]
                baroend = baro.index[-1]
                
                for screen in well.screen_set.all():
                    logger.info(unicode(screen))
                    hasdata = False
                    for ds in screen.mloc.datasource_set.all():
                        for sf in ds.sourcefiles.order_by('start'):
                            fname = os.path.basename(sf.file.name)
                            df = sf.get_data()
                            if isinstance(df,dict):
                                df = df.itervalues().next()
                            if df is None or df.empty:
                                logger.warning('File {} skipped: no data'.format(fname))
                                continue
                                
                            data = df['PRESSURE'].dropna().groupby(df.index).last().sort_index()
                        
                            dataend = data.index[0]
                            if dataend < barostart:
                                logger.warning('File {} skipped: no air pressure data available before {}'.format(fname,barostart))
                                continue

                            datastart = data.index[0]
                            if datastart > baroend:
                                logger.warning('File {} skipped: no air pressure data available after {}'.format(fname,baroend))
                                continue

                            hasdata = True
                            if datastart < barostart:
                                logger.warning('File {} only partly checked: no air pressure data available before {}'.format(fname,barostart))

                            if dataend > baroend:
                                logger.warning('File {} only partly checked: no air pressure data available after {}'.format(fname,baroend))
                
                            adata, abaro = data.align(baro)
                            abaro = abaro.interpolate(method='time')
                            abaro = abaro.reindex(data.index)
                            abaro[:barostart] = np.NaN
                            abaro[baroend:] = np.NaN
                            data = data - abaro
                
                            data.dropna(inplace=True)
                            
                            dry0 = data[data<0].size
                            dry2 = data[data<2].size
                            dry5 = data[data<5].size
                            txt = '{},{},{},{},{},{},{},{}'.format(screen,fname,sf.start,sf.stop,sf.rows,dry0,dry2,dry5)
                            logger.debug(txt)
                            csv.write('{}\n'.format(txt))
                    if not hasdata:
                        # report screen without data
                        csv.write('{},{},{},{},{},{},{},{}\n'.format(screen,'','','',0,-999,-999,-999))
            