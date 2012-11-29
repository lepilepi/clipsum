from datetime import datetime
import numpy as np
import sys
import tables
from core.surf_database import FeatureStore

if __name__ == '__main__':
    """ This tool helps to create HDF file with descriptors
        from sqlite3 database

        Usage:
            python sqlite2hdf.py video.avi

        (It will look for video.avi.db)
    """

    db = FeatureStore(sys.argv[1])
    filename = '%s.surf.hdf' % db.project_name

    n_keypoints = db.c.execute("SELECT COUNT(*) FROM keypoints").fetchone()[0]
    print n_keypoints
    m=np.empty((n_keypoints,137) ,dtype=np.float32)

    print "Starting reading database file and building numpy array..."
    d1 = datetime.now()
    # -------------------------------
    for i, keyp in enumerate(db.c.execute("SELECT * FROM frames INNER JOIN keypoints ON frames.id=keypoints.frame_id")):
#        m[i]= keyp[7:]
        m[i]= keyp[:]
    # -------------------------------
    d2 = datetime.now()
    print "Read complete, elapsed time: %d.%d\n" % ((d2-d1).seconds, (d2-d1).microseconds)

    print "Saving as DHF file..."
    # *******************************
    # Creating CArray for descriptors
    # *******************************
    f = tables.openFile(filename, 'w')
    atom = tables.Atom.from_dtype(m.dtype)
    filters = tables.Filters(complib='blosc', complevel=1)
    descriptors = f.createCArray(f.root, 'descriptors', atom, (len(m),128), filters=filters)

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
    # *******************************************************
    # Fill up keypoints table and descriptors array with data
    # *******************************************************

    d1 = datetime.now()
    print "Bulilding keypoints..."

    for kp in m[:,:9]:
        r = keypoints.row

        r['pos'] = kp[1]
        r['x'] = kp[3]
        r['y'] = kp[4]
        r['laplacian'] = kp[5]
        r['size'] = kp[6]
        r['dir'] = kp[7]
        r['hessian'] = kp[8]
        r.append()

    keypoints.flush()

    d2 = datetime.now()
    print "Table saved. Elapsed time: %d.%d" % ((d2-d1).seconds, (d2-d1).microseconds)

    d1 = datetime.now()

    print "Bulilding descriptors..."

    descriptors[:] = m[:,9:]

    d2 = datetime.now()
    print "Descriptors saved. Elapsed time: %d.%d" % ((d2-d1).seconds, (d2-d1).microseconds)


    d1 = datetime.now()

    print 'Creating indexes'
    f.root.keypoints.cols.x.createIndex()
    f.root.keypoints.cols.y.createIndex()


    d2 = datetime.now()
    print "Indexes created. Elapsed time: %d.%d" % ((d2-d1).seconds, (d2-d1).microseconds)

    f.close()
