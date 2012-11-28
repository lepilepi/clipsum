from datetime import datetime
import cv,cv2
import numpy as np
import sys
import os
import tables
from scipy.cluster.vq import kmeans2 as scipy_kmeans

# -------------------------------
print 'Reading HDF file...'

filename = '%s.surf.hdf' % os.path.basename(sys.argv[1])
f = tables.openFile(filename, 'r')

n_keypoints = f.root.descriptors.nrows
print n_keypoints
m=np.empty((n_keypoints,128) ,dtype=np.float32)

for i,row in enumerate(f.root.descriptors):
    m[i] = row

f.close()
# -------------------------------
K = int(sys.argv[2])

print 'Starting clusterig method...'

d1 = datetime.now()

if sys.argv[3]=='scipy':
    print "Scipy kmeans"
    centroids, labels = scipy_kmeans(m, K, minit='points')
else:
    print "Opencv kmeans"
    samples = cv.fromarray(m)
    labels = cv.CreateMat(samples.height, 1, cv.CV_32SC1)
    crit = (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 10, 1.0)
    cv.KMeans2(samples, K, labels, crit)

d2 = datetime.now()
print "Elapsed time for %d iterations: %d.%d" % (K, (d2-d1).seconds, (d2-d1).microseconds)

import pdb; pdb.set_trace()
