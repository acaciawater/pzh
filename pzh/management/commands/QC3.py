from django.core.management.base import BaseCommand
import os
import logging
import numpy as np
from acacia.meetnet.models import Well
logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'check raw data for QC3'

    def handle(self, *args, **options):
        baros = {}
        with open('QC3.csv','w') as csv:
            csv.write('screen,file,from,to,points,3a-buis,3b-filter,3c-sensor,3d-vol,3e-overloop\n')
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
                    for pos in screen.loggerpos_set.order_by('start_date'):
                        for sf in pos.monfile_set.order_by('start_date'):
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
                            
                            zmaaiveld = screen.well.maaiveld
                            zsensor = pos.refpnt - pos.depth
                            ztopbuis = screen.refpnt
                            zbottombuis = screen.refpnt - screen.depth
                            zbottomfilter = screen.refpnt - screen.bottom
                            
                            level = data / 100.0 + zsensor
                            
                            qc3a = level[level < zbottombuis].count()
                            qc3b = level[level < zbottomfilter].count()
                            qc3c = level[level < zsensor].count()
                            qc3d = level[level > zmaaiveld].count()
                            qc3e = level[level > ztopbuis].count()
                             
                            txt = ','.join(map(str,[screen,fname,sf.start,sf.stop,sf.rows,
                                                    qc3a, qc3b, qc3c, qc3d, qc3e]))
                            logger.debug(txt)
                            csv.write('{}\n'.format(txt))
            