from collections import Counter
import os
import sys
import tables
import numpy as np


x1 = 100
x2 = 300
y1 = 100
y2 = 300
p = 5000


filename = '%s.surf.hdf' % os.path.basename(sys.argv[1])
f = tables.openFile(filename, 'r')


try:
    f.root.clusters
except tables.NoSuchNodeError:
    print "Please run 'cluster_descriptors.py' first!"
    sys.exit(-1)

feature_ids = f.root.keypoints.readWhere(
            '(pos==%d) & (x>%d) & (x<%d) & (y>%d) & (y<%d)' % (p,x1,x2,y1,y2),
            field='cluster')
frame_positions=[getattr(f.root.clusters, 'cluster_%d' % i)[0] for i in feature_ids]

frame_positions=np.concatenate(frame_positions)

cc=Counter(frame_positions)
import pdb;pdb.set_trace()