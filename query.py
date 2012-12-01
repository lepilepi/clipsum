from collections import Counter
import os
import sys
import tables
import numpy as np

def query_region(filename, p, x1,y1, x2,y2):
    filename = '%s.surf.hdf' % os.path.basename(filename)

    try:
        f = tables.openFile(filename, 'r')
    except IOError:
        raise Exception("Please run 'surfdb.py' first!")

    try:
        f.root.clusters
    except tables.NoSuchNodeError:
        raise Exception("Please run 'cluster_descriptors.py' first!")

    feature_ids = f.root.keypoints.readWhere(
            '(pos==%d) & (x>%d) & (x<%d) & (y>%d) & (y<%d)' % (p,x1,x2,y1,y2),
            field='cluster')
    frame_positions=[getattr(f.root.clusters, 'cluster_%d' % i)[0] for i in feature_ids]

    frame_positions=np.concatenate(frame_positions)

    cc=Counter(frame_positions)

    return cc

if __name__ == "__main__":
    result = query_region(sys.argv[1], int(sys.argv[2]),
                                            int(sys.argv[3]),int(sys.argv[4]),
                                            int(sys.argv[5]),int(sys.argv[6]))
    import pdb;pdb.set_trace()