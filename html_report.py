from operator import itemgetter
import sys
import tables
import numpy as np
from jinja2 import Template, Environment, PackageLoader
import os, errno
from core.shots import Shot
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


filename = os.path.basename(sys.argv[1])
hdf_filename = '%s.hdf' % os.path.basename(sys.argv[1])
f = tables.openFile(hdf_filename, 'r+')
clusterings = f.root.clusterings[:]
min_clustering = min(clusterings, key=itemgetter('squared_error'))
clustering_index = np.where(clusterings == min_clustering)

clustering_group = getattr(f.root, 'clustering_%d' % clustering_index, None)

clusters = []
for arr in clustering_group:
    if arr.name.startswith('cluster_'):

        shots = []
        for id in arr[0]:
            shot = Shot(f.root.shots[id][0], f.root.shots[id][1])
            shot.is_result = id in clustering_group.centroids[0]
            shots.append(shot)

        clusters.append(shots)

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
        parser.save_frame(shot.median,
            file_name='report/img/%d.jpg' % shot.median)
        parser.save_frame(shot.median,
                file_name='report/img/%d_thumb.jpg' % shot.median,
                width = 60)


#jinja
env = Environment(loader=PackageLoader('core', 'assets'))
template = env.get_template('index_template.html')
html = template.render(clusters = clusters)
f=open('report/index.html', 'wb')
f.write(html)


