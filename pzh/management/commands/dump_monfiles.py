'''
Created on Dec 28, 2019

@author: theo
'''
import os
import zipfile
import logging
from django.core.management.base import BaseCommand
from acacia.meetnet.models import Well
from acacia.data.util import slugify

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = ''
    help = 'dump all monfiles in zip archives'

    def add_arguments(self, parser):
        parser.add_argument('-d', '--dest',
                action='store',
                dest = 'dest',
                default = '.',
                help = 'destination folder')
                        
    def handle(self, *args, **options):
        ''' dump monfiles ordered by well and by screen '''
        dest = options.get('dest')
        if not os.path.exists(dest):
            os.makedirs(dest)
        for well in Well.objects.all():
            zipname = os.path.join(dest,slugify(well)+'.zip')
            logger.info(zipname)
            with zipfile.ZipFile(zipname,'w') as zf:
                filenames = []
                for screen in well.screen_set.order_by('nr'):
                    for monfile in screen.get_monfiles():
                        basename = os.path.basename(monfile.file.name)
                        filename = os.path.join(slugify(screen),basename).upper() # case insensitive for Microsoft archives
                        if filename in filenames:
                            name, ext = os.path.splitext(filename)
                            for suffix in range(0,26):
                                newname = name+chr(suffix+ord('a'))+ext
                                if not newname in filenames:
                                    filename = newname
                                    break
                        print(filename)
                        zf.write(monfile.file.path,filename)
                        filenames.append(filename)

#     def handle1(self, *args, **options):
#         ''' dump monfiles ordered by serial number of logger '''
#         gen = Generator.objects.get(name='Schlumberger')
#         files = SourceFile.objects.filter(datasource__generator=gen)
#         datasources = gen.datasource_set
#         print('%d datasources, %d sourcefiles' % (datasources.count(), files.count()))
#         with zipfile.ZipFile('monfiles.zip','w') as zf:
#             for datasource in datasources.order_by('name'):
#                 for sourcefile in datasource.sourcefiles.order_by('start'):
#                     basename = os.path.basename(sourcefile.file.name)
#                     filename = datasource.name + '/' + basename
#                     print(filename)
#                     zf.write(sourcefile.file.path,filename)
#                      
