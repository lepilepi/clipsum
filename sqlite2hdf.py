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
    m=np.empty((n_keypoints,128) ,dtype=np.float64)

    print "Starting reading database file and building numpy array..."
    d1 = datetime.now()
    # -------------------------------
    for i, keyp in enumerate(db.c.execute("SELECT * FROM keypoints")):
        m[i]= keyp[7:]
    # -------------------------------
    d2 = datetime.now()
    print "Read complete, elapsed time: %d.%d\n" % ((d2-d1).seconds, (d2-d1).microseconds)


    print "Saving as DHF file..."
    d1 = datetime.now()
    #    ****************************
    f = tables.openFile(filename, 'w')
    atom = tables.Atom.from_dtype(m.dtype)
    filters = tables.Filters(complib='blosc', complevel=1)
    ds = f.createCArray(f.root, 'descriptors', atom, m.shape, filters=filters)
    ds[:] = m
    f.close()
    #    ****************************

    d2 = datetime.now()
    print "Done. Elapsed time: %d.%d" % ((d2-d1).seconds, (d2-d1).microseconds)
