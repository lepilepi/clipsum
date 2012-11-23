import sys
from core.database import ProjectInfo
from jinja2 import Template, Environment, PackageLoader
import os, errno
from core.videoparser import VideoParser

def mkdir_p(path):
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise

import shutil, errno

def copyanything(src, dst):
    try:
        shutil.copytree(src, dst)
    except OSError as exc: # python >2.5
        if exc.errno == errno.ENOTDIR:
            shutil.copy(src, dst)
        elif exc.errno == errno.EEXIST:
            pass
        else: raise



filename = sys.argv[1]
project = ProjectInfo(filename)

id=project.best_clustering_id()
clusters = project.clusters(id)

shutil.rmtree('report/css', ignore_errors=True)
shutil.rmtree('report/images', ignore_errors=True)
shutil.rmtree('report/js', ignore_errors=True)

mkdir_p('report')
mkdir_p('report/img')
copyanything('core/assets/css','report/css')
copyanything('core/assets/images','report/images')
copyanything('core/assets/img','report/img')
copyanything('core/assets/js','report/js')

#generate thumbnails
parser = VideoParser(filename)
for i,cluster in enumerate(clusters):
    print "%d of %d" % (i, len(clusters))
    for shot in cluster:
        parser.save_frame_msec(shot.median(),
            file_name='report/img/%d.jpg' % shot.median())
        parser.save_frame_msec(shot.median(),
                file_name='report/img/%d_thumb.jpg' % shot.median(),
                width = 60)


#jinja
env = Environment(loader=PackageLoader('core', 'assets'))
template = env.get_template('index_template.html')
html = template.render(clusters = clusters)
f=open('report/index.html', 'wb')
f.write(html)


