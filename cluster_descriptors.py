import cv,cv2
import numpy as np
import sys
import os
import tables

# -------------------------------
print 'Reading HDF file...'

filename = '%s.surf.hdf' % os.path.basename(sys.argv[1])
f = tables.openFile(filename, 'r')

n_keypoints = f.root.descriptors.nrows
print n_keypoints
m=np.empty((n_keypoints,128) ,dtype=np.float64)

for i,row in enumerate(f.root.descriptors):
    m[i] = row

f.close()
# -------------------------------
K = int(sys.argv[2])

print 'Starting clusterig method...'

h,w = m.shape
samples = cv.CreateMat(h, w, cv.CV_32FC3)

labels = cv.CreateMat(samples.height, 1, cv.CV_32SC1)

crit = (cv.CV_TERMCRIT_EPS + cv.CV_TERMCRIT_ITER, 10, 1.0)
cv.KMeans2(samples, K, labels, crit)

import pdb; pdb.set_trace()
