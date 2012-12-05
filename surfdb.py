import sys
from core.videoparser import VideoParser
from datetime import datetime
import tables
import os
import numpy as np

if __name__ == '__main__':
    parser = VideoParser(sys.argv[1])

    filename = '%s.surf.hdf' % os.path.basename(sys.argv[1])
    f = tables.openFile(filename, 'w')
    # *****************************
    # Creating tables for keypoints
    # *****************************
    schema = {
        'pos':      tables.IntCol(pos=1),
        'x':        tables.FloatCol(pos=2),
        'y':        tables.FloatCol(pos=3),
        'laplacian':tables.IntCol(pos=4),
        'size':     tables.IntCol(pos=5),
        'dir':      tables.FloatCol(pos=6),
        'hessian':  tables.FloatCol(pos=7),
        'cluster':  tables.IntCol(dflt=-1, pos=8),
        }
    f.createTable('/', 'keypoints', schema)
    keypoints=f.root.keypoints

    # initialize numpy arra in memory
    m = np.array([], dtype=np.float32)

    d1 = datetime.now()

    total = parser.total_frames
    print "Extracting keypoints form frames..."
    for frame_pos in range(0, total, 25):
        print "frame %d of %d (%f%%)"  % (frame_pos, total, frame_pos/float(total)*100)

        (k,d) = parser.surf_frame(frame_pos)
        for k,d in zip(k,d):

            # add keypoint record
            r = keypoints.row
            r['pos'] = frame_pos
            r['x'] = k[0][0]
            r['y'] = k[0][1]
            r['laplacian'] = k[1]
            r['size'] = k[2]
            r['dir'] = k[3]
            r['hessian'] = k[4]
            r.append()

            # append decsriptor to the memory object
            m.resize(len(m)+1, 128)
            m[len(m)-1] = d[:]

    keypoints.flush()

    print 'Building descriptors...'

    # *******************************
    # Creating CArray for descriptors
    # *******************************
    atom = tables.Atom.from_dtype(m.dtype)
    filters = tables.Filters(complib='blosc', complevel=1)
    descriptors = f.createCArray(f.root, 'descriptors', atom, (len(m),128), filters=filters)
    descriptors[:] = m[:]

    print 'Creating indexes...'
    f.root.keypoints.cols.x.createIndex()
    f.root.keypoints.cols.y.createIndex()

    d2 = datetime.now()
    print "Done. Elapsed time: %d.%d" % ((d2-d1).seconds, (d2-d1).microseconds)


