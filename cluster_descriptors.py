from datetime import datetime
import cv,cv2
import numpy as np
import sys
import os
import tables
from scipy.cluster.vq import kmeans2 as scipy_kmeans

# -------------------------------
print 'Reading HDF file...'

d1 = datetime.now()

filename = '%s.surf.hdf' % os.path.basename(sys.argv[1])
f = tables.openFile(filename, 'r')

n_keypoints = f.root.descriptors.nrows
print n_keypoints
m=np.empty((n_keypoints,128) ,dtype=np.float32)

for i,row in enumerate(f.root.descriptors):
    m[i] = row

f.close()
del f

d2 = datetime.now()
print "Loading time was: %d.%d" % ((d2-d1).seconds, (d2-d1).microseconds)
# -------------------------------
K = int(sys.argv[2])

print 'Starting clusterig method...'

d1 = datetime.now()

if len(sys.argv)>3 and sys.argv[3]=='scipy':
    print "Scipy kmeans"
    centroids, labels = scipy_kmeans(m, K, minit='points')
else:
    print "Opencv kmeans"
    samples = cv.fromarray(m)
    labels = cv.CreateMat(samples.height, 1, cv.CV_32SC1)
#    crit = (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 10, 1.0)
    crit = (cv.CV_TERMCRIT_ITER, 10)
    cv.KMeans2(samples, K, labels, crit)


d2 = datetime.now()
print "Elapsed time for %d clusters: %d.%d" % (K, (d2-d1).seconds, (d2-d1).microseconds)

print 'Updating HDF file with results...'

d1 = datetime.now()

labels = np.asarray(labels)
f = tables.openFile(filename, 'r+')
for i,row in enumerate(f.root.keypoints):
    row['cluster']=labels[i]
    row.update()

d2 = datetime.now()
print "Done: %d.%d" % ((d2-d1).seconds, (d2-d1).microseconds)


print 'Building inverted index...'

d1 = datetime.now()
try:
    f.root.clusters._f_remove(recursive=1)
except tables.NoSuchNodeError:
    pass
f.createGroup(f.root, 'clusters')

for cluster_id in range(K):
    data = list(set(f.root.keypoints.readWhere('cluster==%d' % cluster_id, field='pos')))

    filters = tables.Filters(complib='blosc', complevel=1)
    descriptors = f.createCArray(f.root.clusters, "cluster_%d" % cluster_id, tables.Int32Atom(), (1,len(data)), filters=filters)
    descriptors[:] = data[:]

d2 = datetime.now()
print "Building time was: %d.%d" % ((d2-d1).seconds, (d2-d1).microseconds)


import pdb; pdb.set_trace()
f.close()
